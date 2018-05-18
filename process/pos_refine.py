"""
"""

#! /usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# make an example cxi file
# with a small sample and small aberations

import sys, os
base = os.path.join(os.path.dirname(__file__), '..')
root = os.path.abspath(base)
sys.path.insert(0, os.path.join(root, 'utils'))

#import pyximport; pyximport.install()
import feature_matching as fm
import cmdline_config_cxi_reader
from mpiarray import MpiArray
from mpiarray import MpiArray_from_h5

import math
import numpy as np
import h5py
from scipy.ndimage.filters import gaussian_filter

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from grad_descent import build_atlas_distortions_MpiArray, mk_reg

def forward_frame(atlas, W, R, u, ij=None):
    # the regular pixel values
    if ij is None :
        ij = np.ogrid[0:W.shape[0], 0:W.shape[1]]
    If = W*fm.forward_frame(atlas, W, R, u, ij, sub_pixel = True)
    return If

def forward_error(atlas, W, R, u, frame, ij=None):
    If  = forward_frame(atlas, W, R, u, ij)
    m   = (If>0)*(frame>0)*(W>0)
    err = np.sum((If[m] - frame[m])**2) / np.sum(m)
    return err

def pos_refine(atlas, W, R, u, frame, 
               bounds=[(0., 10.), (0., 10.)], max_iters=1000):
    ij = np.ogrid[0:W.shape[0], 0:W.shape[1]]
    def fun(x):
        err = forward_error(atlas, W, R+x, u, frame, ij)
        return err
    
    x0   = np.array([0., 0.])
    err0 = fun(x0)
    options = {'maxiter' : max_iters, 'eps' : 0.1, 'xatol': 0.1}
    from scipy.optimize import minimize
    res = minimize(fun, x0, bounds = bounds, 
                   options = {'maxiter' : max_iters, 'eps' : 0.1, 'xatol': 0.1})

    #from scipy.optimize import basinhopping
    #options = {'maxiter' : max_iters, 'eps' : 0.1, 'xatol': 0.1}
    #res = basinhopping(fun, x0, niter=5, T=100, stepsize=5, 
    #        minimizer_kwargs={'bounds': bounds, 'options': options})
    if rank == 0 : print(err0, res); sys.stdout.flush()
    R += res.x
    return R, res.fun

def pos_refine_grid(atlas, W, R, u, frame, 
               bounds=[(0., 10.), (0., 10.)], max_iters=1000, 
               sub_pixel = False):
    ij = np.ogrid[0:W.shape[0], 0:W.shape[1]]
    def fun(x):
        err = forward_error(atlas, W, R+x, u, frame, ij)
        return err
    
    k = np.arange(int(bounds[0][0]), int(bounds[0][1])+1, 1)
    l = np.arange(int(bounds[0][0]), int(bounds[0][1])+1, 1)
    k, l = np.meshgrid(k, l, indexing='ij')
    shape = k.shape
    kl = np.vstack((k.ravel(), l.ravel())).T
    
    x0   = np.array([0., 0.])
    err0 = fun(x0)

    errs = np.array( [fun(x) for x in kl] )
    
    i = np.argmin(errs)
    x = kl[i]
    
    if rank == 0 : print(err0, errs[i], x); sys.stdout.flush()
    R += x
    err = errs[i]

    if sub_pixel :
        R, err = pos_refine(atlas, W, R, u, frame, 
                            [(-1, 1), (-1, 1)], max_iters)
    return R, err

def pos_refine_all(atlas, W, R, u, I, 
                   bounds=[(0., 10.), (0., 10.)], max_iters=1000,
                   sub_pixel = False):
    R_out = []
    err_out = []
    for r, frame in zip(R.arr, I.arr):
        r_out, err = pos_refine_grid(atlas, W, r, u, frame, bounds, max_iters, sub_pixel)
        R_out.append(r_out.copy())
        err_out.append(err)
    
    Rs   = MpiArray(np.array(R_out), axis=0)
    errs = MpiArray(np.array(err_out), axis=0)
    return Rs, errs

def get_input():
    args, params = cmdline_config_cxi_reader.get_all('pos_refine', 
                   'update the sample translations according to a least squares minimisation procedure',
                   exclude=['frames'])
    params = params['pos_refine']
    
    # frames, split by frame no.
    roi = params['roi']
    roi = [params['good_frames'], slice(roi[0],roi[1]), slice(roi[2],roi[3])]
    params['frames']     = MpiArray_from_h5(args.filename, params['frames'], 
                                            axis=0, dtype=np.float64, roi=roi)
    #params['frames'] = params['frames'][params['good_frames']]
    
    if rank != 0 :
        params['R_ss_fs']    = None 
    
    params['R_ss_fs']  = MpiArray(params['R_ss_fs'])
    params['R_ss_fs'].scatter(axis=0)
     
    # set masked pixels to negative 1
    for i in range(params['frames'].arr.shape[0]):
        params['frames'].arr[i][~params['mask']] = -1
    
    params['whitefield'][~params['mask']]    = -1 
    
    if params['pixel_shifts'] is None :
        params['pixel_shifts'] = np.zeros((2,) + params['whitefield'].shape, dtype=np.float64)
    
    # add a regularization factor
    shape = params['whitefield'].shape
    reg   = mk_reg(shape, params['reg'])
    
    return args, params, reg

if __name__ == '__main__':
    args, params, reg = get_input()
    
    # merge the frames
    if params['atlas'] is None :
        atlas, params['R_ss_fs'] = build_atlas_distortions_MpiArray(params['frames'], 
                                                  params['whitefield'], 
                                                  params['R_ss_fs'], 
                                                  params['pixel_shifts'], 
                                                  reg=reg,
                                                  return_steps = True)
    else :
        atlas = params['atlas']
    
    if params['atlas_smooth'] is not None and params['atlas_smooth'] is not 0 :
        atlas = gaussian_filter(atlas, params['atlas_smooth'])
    
    # refine the positions
    m = params['max_step']
    params['R_ss_fs'], errs = pos_refine_all(atlas, params['whitefield'], 
                                       params['R_ss_fs'], 
                                       params['pixel_shifts'], 
                                       params['frames'], 
                                       bounds=[(-m, m), (-m, m)], 
                                       max_iters=params['max_iters'],
                                       sub_pixel = params['sub_pixel'])
     
    errs2    = errs.allgather()
    em       = errs2.mean()
    weights  = np.abs(errs.arr-em)
    weights  = 1. - weights / weights.max() + 0.2
    weights  = MpiArray(weights, axis=0)
    
    atlas  = build_atlas_distortions_MpiArray(params['frames'], 
                                              params['whitefield'], 
                                              params['R_ss_fs'], 
                                              params['pixel_shifts'], 
                                              reg=reg, weights = weights.arr)
    
    params['R_ss_fs'] = params['R_ss_fs'].gather()
    errs    = errs.gather()
    weights = weights.gather()
    
    # real-time output
    if rank == 0 :
        out = {'R_ss_fs' : params['R_ss_fs'], 'atlas' : atlas, 
               'errs' : errs, 'weights' : weights}
        cmdline_config_cxi_reader.write_all(params, args.filename, out)
        print('display: '+params['h5_group']+'/R_ss_fs') ; sys.stdout.flush()
    

