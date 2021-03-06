#!/usr/bin/env python
import os
import speckle_tracking as st
from speckle_tracking import cmdline_config_cxi_reader
from speckle_tracking import cmdline_parser 

import numpy as np

def main(overide={}):
    # get command line args and config
    sc  = 'update_translations'
     
    # search the current directory for *.ini files if not present in cxi directory
    config_dirs = [os.path.split(os.path.abspath(__file__))[0]]
    
    # extract the first paragraph from the doc string
    des = st.make_object_map.__doc__.split('\n\n')[0]
    
    # now load the necessary data
    args, params = cmdline_config_cxi_reader.get_all(sc, des, config_dirs=config_dirs, roi=True)
    params = params[sc]

    # overide with input params (if any)
    params.update(overide)
    
    dij_n = st.update_translations(params['data'].astype(np.float32),
                                   params['mask'],
                                   params['whitefield'],
                                   params['pixel_translations'],
                                   params['reference_image'],
                                   params['pixel_map'],
                                   params['n0'],
                                   params['m0'],
                                   params['sw_ss'],
                                   params['sw_fs'],
                                   params['ls'])
    
    comp = np.array([dij_n, params['pixel_translations']])
    
    out = {'pixel_translations': dij_n, 
           'pixel_translations_comparison': comp}
    cmdline_config_cxi_reader.write_all(params, args.filename, out, apply_roi=True)
    
    # output display for gui
    with open('.log', 'w') as f:
        print('display: '+params['h5_group']+'/pixel_translations_comparison scatter', file=f)


if __name__ == '__main__':
    main()
