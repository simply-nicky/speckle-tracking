Thon Rings
==========
If you look at the defocused image of a thin sample with phase contrast, then you will see Fresnel fringes around the edges. See, for example, this image from the :ref:`siemens_star` tutorial:

.. image:: images/siemens_fringes.png
   :width: 200

Now these fringes will become broader the closer the object is to the focus, and more fine the further away it is. So they are a useful means to determine this information. Of course this method relies on our ability to actually see the fringes, if the coherence of the beam is too low, or the sample wobbles during the exposure, then these fringes will be washed out. 

Simple
------
Let's assume that we have:

1. A thin weakly scattering object: :math:`T(r) = |T(r)| e^{i\phi(r)} \approx 1 + i\phi(r)`, and
2. that plane wave light of wavelength :math:`\lambda` passes through it,
3. a pixilated detector imaging the intensity a distance z from the sample.

Let us now see what the defocused image looks like, ignoring terms of order :math:`\phi^2`:

.. math::
    
    \begin{align}
    I(r) &= \big| T(r) \otimes e^{i\pi \frac{r^2}{\lambda z}} \big|^2 \\ 
                &\approx 1 - 2 \Im\left\{\phi(r) \otimes e^{i\pi \frac{r^2}{\lambda z}}\right\} 
    \end{align}
    
Now take the Fourier transform of the defocused image to see the rings:

.. math::
    
    \begin{align}
    \mathcal{F}[I](q) &\approx \delta(q) + 2 \sin(\pi \lambda z q^2)\hat{\phi}(q)
    \end{align}

.. image:: images/siemens_thon.png
   :width: 300

The above image was actually made from:

.. math::
    
    \begin{align}
    \text{image}(q) &= \sum_n \big|\mathcal{F}[M(r) e^{-r^2 / 2 \sigma^2} I_n(r) / W(r) ](q) \big|^2
    \end{align}

where :math:`n` is the image number, :math:`M(r)` is the mask, :math:`W(r)` is the whitefield, and the Gaussian is applied to avoid Fourier aliasing artefacts. The image was then taken to the power of 0.1 to enhance the contrast.

More complex
------------
But, what if the sample is on a subtrate, or there is some absorption contrast? Also, we are looking at magnified projection images that have distortions...

.. math::
    
    \begin{align}
    T(r) &= |T(r)| e^{i\phi(r) + i\phi_\text{sub}}  &&\text{substrate phase shift added} \\
         &\approx e^{-i\frac{2\pi}{\lambda} t(r) (\delta_\lambda - i \beta_\lambda) + i\phi_\text{sub}}  &&\text{projection approximation for a single material } \\
         &             && \text{of thickness t(r) and refractive index } \delta_\lambda - i \beta_\lambda \\
         &\approx e^{i\phi_\text{sub}}\left(1-i\frac{2\pi}{\lambda} t(r) (\delta_\lambda - i \beta_\lambda)\right) &&\text{expanded to first order in t}
    \end{align}


So we have:

.. math::
    
    \begin{align}
    I^\infty(r, z) &= \big| T(r) \otimes e^{i\pi \frac{r^2}{\lambda z}} \big|^2 \\ 
                     &\approx 1 - \frac{4\pi\delta_\lambda}{\lambda}\Im \left\{  t(r) \otimes e^{i\pi \frac{r^2}{\lambda z}}\right\} - \frac{4\pi\beta_\lambda}{\lambda}\Re \left\{ t(r) \otimes e^{i\pi \frac{r^2}{\lambda z}}\right\} 
    \end{align}

The overall phase shift from the substrate is factored out, obviously. Note that here I've assumed that the sample is sitting on top of the subtrate, so every x-ray gets the same phase shift. But if the sample where embedded in the subtrate, for example in ice, then it's a different story.

Taking the Fourier transform of the intensity gives:

.. math::
    
    \begin{align}
    \hat{I}^\infty(q, z) &\approx \delta(q) + \frac{4\pi}{\lambda} \hat{t}(q) \left( \delta_\lambda \sin(\pi\lambda z q^2) - \beta_\lambda \cos(\pi\lambda z q^2)\right)
    \end{align}

The complicating factor here, is that if we are looking at magnified projection images rather than just a plane wave illuminated sample, then z will actually effect the above function **and** the magnification.  

By the Fresnel scaling theorem we have that :math:`I^{z_1}(r, z_2) = M^{-2}I^\inf(r/M, z_2/M)`, where :math:`z_1` is the focus to sample distance, :math:`z_2` is the sample to detector distance and :math:`M=(z_1+z_2)/z_1`. If we set :math:`z_D = z_1 + z_2` as the focus to sample distance then we have:

.. math::
    
    \begin{align}
    I^{z_1}(x, y, z_D-z_1) &= (z_D / z_1)^2 I^\infty(x z_1 / z_D, y z_1 / z_D, (z_D-z_1) z_1 / z_D) \\
                           &= (z_D / z_1)^2 I^\infty(x', y', z_\text{eff}) \\
    \end{align}

and, ignoring the scalling factor, we therefore have:

.. math::
    
    \begin{align}
    \hat{I}^{z_1}(q_x, q_y, z_D-z_1) &= \hat{I}^\infty(q_x z_D / z_1, q_y z_D / z_1, (z_D-z_1) z_1 / z_D) \\
    &\approx \frac{4\pi}{\lambda} \hat{t}(q') \left( \delta_\lambda \sin(\pi\lambda z_\text{eff} q'^2) - \beta_\lambda \cos(\pi\lambda z_\text{eff} q'^2)\right) \quad \text{for } q_x,q_y \neq 0 \\
    \text{with } z_\text{eff} q'^2 &= \frac{(z_D-z_1)z_D}{z_1}q^2
    \end{align}

Fitting
-------
One problem with trying to fit the above equation for z_1 is that we don't know t. Furthermore, :math:`\hat{t}(q)` is just as likely to be positive as it is negative. So if we average over many frames and the azimuthal angle then we may just cancel out the signal we are trying to fit. So let's take the square of each power spectrum before averaging over frame number and angle. So our new target function is:

.. math::
    
    \begin{align}
    f(q, z_1) &= \sum_n \int_0^{2\pi} \big| \hat{I}_n^{z_1}(q_x, q_y, z_D-z_1)\big|^2 d\theta_q \\
    &=  \left( \sin(\pi\lambda z_\text{eff} q'^2) - \frac{\beta_\lambda}{\delta_\lambda} \cos(\pi\lambda z_\text{eff} q'^2)\right)^2 \sum_n \int_0^{2\pi} \big| \frac{4\pi\delta_\lambda}{\lambda} \hat{t}_n(q') \big|^2 d\theta_q + b(q)
    \end{align}

where I have also added a q-dependent background term for safe keeping.

Background and Envelope estimation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For now let us assume that :math:`\beta_\lambda=0` and make an initial estimate for :math:`z_1`. Given these assumptions we can use the fact that:

.. math::
    
    \begin{align}
    \sin^2(\pi\lambda z_\text{eff} q'^2) &= 0  & \text{for } q_n &= \sqrt{ \frac{n z_1}{\lambda z_D(z_D-z_1)} } \\
    \sin^2(\pi\lambda z_\text{eff} q'^2) &= 1  & \text{for } q_m &= \sqrt{ \frac{(m+1/2) z_1}{\lambda z_D(z_D-z_1)} } \\
    \end{align}

to estimate a smooth background, which can be subtracted, as well as the envelope function in the previous equation.  


.. math::
    
    \begin{align}
    b(q) \approx &(q_n - q) f(q_{n-1}, z_1) + (q - q_{n-1}) f(q_{n}, z_1)  &&\text{for } q_{n-1} < q < q_n\\
    \sum_n \int_0^{2\pi} \big| \frac{4\pi\delta_\lambda}{\lambda} \hat{t}_n(q') \big|^2 d\theta_q \approx &(q_m - q) [f(q_{m-1}, z_1)-b(q_{m-1})] \\
    + &(q - q_{m-1}) [f(q_{m}, z_1)-b(q_{m})]  &&\text{for } q_{m-1} < q < q_m\\
    \end{align}

Discreet Formalism
------------------

So what is the sampling of q? By the Fresnel scaling theorem we have that :math:`I^{z_1}(r, z_2) = M^{-2}I^\inf(r/M, z_2/M)`, where :math:`z_1` is the focus to sample distance, :math:`z_2` is the sample to detector distance and :math:`M=(z_1+z_2)/z_1`. If we set :math:`z_D = z_1 + z_2` as the focus to sample distance then we have:

.. math::
    
    \begin{align}
    I^{z_1}(i\Delta x, j\Delta y, z_D-z_1) &= I^\infty(i\Delta x z_1 / z_D, j\Delta y z_1 / z_D, (z_D-z_1) z_1 / z_D) \\
                                               &= I^\infty(i\Delta x_x, j\Delta y', z_\text{eff}) \\
    \end{align}

where :math:`\Delta x` and :math:`\Delta y` are the (real) x and y dimensions of each detector pixel. So when we look at the power stectrum we see:

.. math::
    
    \begin{align}
    \hat{I}^{z_1}(\frac{i}{N\Delta x}, \frac{j}{M\Delta y}, z_D-z_1) &= \hat{I}^\infty(\frac{i}{N\Delta x'}, \frac{j}{M\Delta y'}, z_\text{eff}) \\
    &\approx \frac{4\pi}{\lambda} \hat{t}(q_{ij}) \left( \delta_\lambda \sin(\pi\lambda z_\text{eff} q_{ij}^2) - \beta_\lambda \cos(\pi\lambda z_\text{eff} q_{ij}^2)\right) \quad \text{for } i,j \neq 0 \\
    z_\text{eff} q_{ij}^2 &= \frac{(z_D-z_1)z_1}{z_D} \frac{z_D^2}{z_1^2}\left(\frac{i^2}{N^2\Delta x^2}+ \frac{j^2}{M^2\Delta y^2}\right) \\
    &= \frac{(z_D-z_1)z_D}{z_1}\left(\frac{i^2}{N^2\Delta x^2}+ \frac{j^2}{M^2\Delta y^2}\right) \\
    \end{align}

where N and M are number of pixels along the x and y dimensions of the detector respectively. 

Fitting
^^^^^^^
One problem with trying to fit the above equation for z_1 is that we don't know t. Furthermore, :math:`\hat{t}(q)` is just as likely to be positive as it is negative. So if we average over many frames and the azimuthal angle then we may just cancel out the signal we are trying to fit. So let's take the square of each power spectrum before averaging over frame number and angle. Given this our new target function is:

.. math::
    
    \begin{align}
    f(i, z_D-z_1) &= \sum_n \sum_{\sqrt{l^2+k^2}=i} \hat{I}^{z_1}_n(\frac{l}{N\Delta x}, \frac{k}{M\Delta y}, z_D-z_1) \\
    &\approx \sum_n \sum_{\sqrt{l^2+k^2}=i}
    \end{align}

