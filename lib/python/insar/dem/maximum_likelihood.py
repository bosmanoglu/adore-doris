# -maximum_likelihood.py- coding: utf-8 -*-
"""
Created on Fri Sep  3 10:46:50 2010

@author: bosmanoglu

After:
M. Eineder
N. Adam

Maximum-Likelihood Estimator to Simultaneously Unwrap, Geocode and Fuse SAR Interferograms
From Different Viewing Geometries Into One Digital Elevation Model
"""

#import numpy as np
from insar import *
from numpy import *
import basic

def radar_coord_dem(dem, i12s, cohs, h2phs, dem_std=10, ref=None, multilook=1, samples=1000, stepsize=None, study_area=None):
    """radar_coord_dem(dem, i12s, cohs, dem_std=10, ref=None):
    dem:  [M,N]
    i12s: [K,M,N]
    cohs: [K,M,N]
    h2phs: [K,M,N]
    dem_std: scalar or [M,N]
    ref: None or tuple (m,n)
    multilook: level of SAR multilooking
    samples=1000, number of samples for search domain
    stepsize= height sensitivity to use instead of samples to constract search space.
    study_area= [m0, mM, n0, nN] 
    """
    z_ref=dem[ref[0],ref[1]];
    dem=dem-z_ref;  #zero reference
    i12s=i12s*tile( conj(i12s[:,ref[0],ref[1]]), (i12s.shape[2], i12s.shape[1], 1) ).T   #zero reference
    if study_area is not None:
        dem  = dem [study_area[0]:study_area[1], study_area[2]:study_area[3]]
        i12s = i12s[:, study_area[0]:study_area[1], study_area[2]:study_area[3]]
        cohs = cohs[:, study_area[0]:study_area[1], study_area[2]:study_area[3]]
        h2phs=h2phs[:, study_area[0]:study_area[1], study_area[2]:study_area[3]]
        if size(dem_std) != 1:
            dem_std=dem_std[study_area[0]:study_area[1], study_area[2]:study_area[3]]
    M,N=dem.shape
    z=zeros(dem.shape); #initialize output
    if size(dem_std) == 1:
        #scalar dem_std convert to array
        dem_std=ones(dem.shape)*dem_std
    elif size(dem_std) != size(dem):
        #dem and dem_std has to be the same size
        print 'DEM_STD has to be a scalar or the same size as DEM.'
        return -1
        
    t=0;
    for m in xrange(M):
        for n in xrange(N):
            z[m,n]=point_solve_dem(dem[m,n], i12s[:,m,n], cohs[:,m,n], h2phs[:,m,n], dem_std[m,n], multilook, samples=samples, stepsize=stepsize);
        if basic.progresstime(t0=t,timeSpan=30):
            t=basic.time.time()
            basic.progress(p=m,t=M,f="%.3f ")        
    z=z+z_ref
    return z

def radar_coord_dem_parallel(dem, i12s, cohs, h2phs, dem_std=10, ref=None, multilook=1, samples=1000, stepsize=None):
    """radar_coord_dem(dem, i12s, cohs, dem_std=10, ref=None):
    dem:  [M,N]
    i12s: [K,M,N]
    cohs: [K,M,N]
    h2phs: [K,M,N]
    dem_std: scalar or [M,N]
    ref: None or tuple (m,n)
    multilook: level of SAR multilooking
    samples=1000, number of samples for search domain
    stepsize= height sensitivity to use instead of samples to constract search space. 
    """
    print "Initializing..."
    import IPython.parallel as parallel
    #from IPython.parallel import Client
    c = parallel.Client()
    lv = c.load_balanced_view() 

    #global dem, i12s, cohs, h2phs, multilook, samples, stepsize
    
    z_ref=dem[ref[0],ref[1]];
    dem=dem-z_ref;  #zero reference
    i12s=i12s*tile( conj(i12s[:,ref[0],ref[1]]), (i12s.shape[2], i12s.shape[1], 1) ).T   #zero reference
    M,N=dem.shape
    z=zeros(dem.shape); #initialize output
    if size(dem_std) == 1:
        #scalar dem_std convert to array
        dem_std=ones(dem.shape)*dem_std
    elif size(dem_std) != size(dem):
        #dem and dem_std has to be the same size
        print 'DEM_STD has to be a scalar or the same size as DEM.'
        return -1   

#    def parfunc(d,i,c,h,ds,m,s,ss):
#        return point_solve_dem(d,i,c,h,ds,m,s,ss)
    
    print "Processing started..."    
    tasks=[]       
    t=basic.time.time() 
              
    for m in xrange(M):
        for n in xrange(N):
            tasks.append(lv.apply(point_solve_dem, dem[m,n], i12s[:,m,n], cohs[:,m,n], h2phs[:,m,n], dem_std[m,n], multilook, samples, stepsize))
            #tasks.append(lv.apply(parfunc, dem[m,n], i12s[:,m,n], cohs[:,m,n], h2phs[:,m,n], dem_std[m,n], multilook, samples, stepsize))
        if progresstime(t0=t,timeSpan=30):
            t=basic.time.time()
            basic.progress(p=m,t=M,f="%.3f ") 
        try:       
            zm = [task.get(60) for task in tasks] # blocks until all results are back
        except parallel.error.TimeoutError:
            zm=[];#restart from the beginning
            k=-N;
            for task in tasks:
                try:
                    zm.append(task.get(1))
                except parallel.error.TimeoutError:
                    print ["Problem on line/pixel: ", m, N+k]
                    zm.append(nan); #if still not ready skip                    
                    lv.abort(lv.history[k])
                    k=k+1                    
        z[m,:]=array(zm).reshape(1,dem.shape[1])
        tasks=[]
        #clean up so that we don't run out of memory
        lv.results.clear()
        c.results.clear()
        c.metadata.clear()
        c.purge_results(targets=c.ids)
    z=z+z_ref    
       
    return z

def radar_coord_dem_parallel2(dem, i12s, cohs, h2phs, dem_std=10, ref=None, multilook=1, samples=1000, stepsize=None):
    """radar_coord_dem(dem, i12s, cohs, dem_std=10, ref=None):
    dem:  [M,N]
    i12s: [K,M,N]
    cohs: [K,M,N]
    h2phs: [K,M,N]
    dem_std: scalar or [M,N]
    ref: None or tuple (m,n)
    multilook: level of SAR multilooking
    samples=1000, number of samples for search domain
    stepsize= height sensitivity to use instead of samples to constract search space. 
    """
    print "Initializing..."
    import parallel
    
    z_ref=dem[ref[0],ref[1]];
    dem=dem-z_ref;  #zero reference
    i12s=i12s*tile( conj(i12s[:,ref[0],ref[1]]), (i12s.shape[2], i12s.shape[1], 1) ).T   #zero reference
    M,N=dem.shape
#    z=zeros(dem.shape); #initialize output
    if size(dem_std) == 1:
        #scalar dem_std convert to array
        dem_std=ones(dem.shape)*dem_std
    elif size(dem_std) != size(dem):
        #dem and dem_std has to be the same size
        print 'DEM_STD has to be a scalar or the same size as DEM.'
        return -1   

#    def parfunc(d,i,c,h,ds,m,s,ss):
#        return point_solve_dem(d,i,c,h,ds,m,s,ss)
    
    print "Processing started..."    
              
    def parfunc(N,d,i,c,h,ds,m,s,ss):
        import insar
        zm=zeros(1,N);
        for n in xrange(N):
            zm[:]=insar.dem.maximum_likelihood.point_solve_dem(d[n],i[:,n],c[:,n],h[:,n],ds[n],m,s,ss)
        return zm
    z=parallel.parfor(r_[0:M], dict(parfunc=parfunc), 'parfunc(dem[l,:], i12s[:,l,:], cohs[:,l,:], h2phs[:,l,:], dem_std[l,:], multilook, samples, stepsize)', 
                      dict(dem=dem, i12s=i12s,cohs=cohs, h2phs=h2phs, dem_std=dem_std, multilook=multilook, samples=samples, stepsize=stepsize))
    z=array(z)
    z=z+z_ref           
    return z


def radar_coord_dem_parallel3(dem, i12s, cohs, h2phs, dem_std=10, ref=None, multilook=1, samples=1000, stepsize=None):
    """radar_coord_dem(dem, i12s, cohs, dem_std=10, ref=None):
    dem:  [M,N]
    i12s: [K,M,N]
    cohs: [K,M,N]
    h2phs: [K,M,N]
    dem_std: scalar or [M,N]
    ref: None or tuple (m,n)
    multilook: level of SAR multilooking
    samples=1000, number of samples for search domain
    stepsize= height sensitivity to use instead of samples to constract search space. 
    """
    print "Initializing..."
    import parallel        
    
    z_ref=dem[ref[0],ref[1]];
    dem=dem-z_ref;  #zero reference
    i12s=i12s*tile( conj(i12s[:,ref[0],ref[1]]), (i12s.shape[2], i12s.shape[1], 1) ).T   #zero reference
    M,N=dem.shape
    idx=(isnan(cohs).sum(0)>=1)
#    z=zeros(dem.shape); #initialize output
    if size(dem_std) == 1:
        #scalar dem_std convert to array
        dem_std=ones(dem.shape)*dem_std
    elif size(dem_std) != size(dem):
        #dem and dem_std has to be the same size
        print 'DEM_STD has to be a scalar or the same size as DEM.'
        return -1   

#    def parfunc(d,i,c,h,ds,m,s,ss):
#        return point_solve_dem(d,i,c,h,ds,m,s,ss)
    
    print "Processing started..."    
              
    def parfunc(k):
        import basic
        import insar
        l,m=basic.ind2sub(dem.shape, k)
        n=~basic.isnan(cohs[:,l,m])
        zm=insar.dem.maximum_likelihood.point_solve_dem(dem[l,m], i12s[n,l,m], cohs[n,l,m], h2phs[n,l,m], dem_std[l,m], multilook=multilook, samples=samples, stepsize=stepsize)
        return zm
    zidx=parallel.map(idx[0], parfunc, dict(dem=dem, i12s=i12s,cohs=cohs, h2phs=h2phs, dem_std=dem_std, multilook=multilook, samples=samples, stepsize=stepsize))
    z=dem.copy()
    z[idx[0]]=zidx; 
    z=z+z_ref           
    return z
        
def pdf_dem(z, z_domain, std_dem):
    """pdf_dem(z, z_domain, std_dem)
    """    
    return exp(-(z-z_domain)**2/2/std_dem**2)/(sqrt(2*pi*std_dem)) 
    
def point_solve_dem(dem, i12s, cohs, h2phs, dem_std, multilook, samples=1000, stepsize=None, figures=False, unwrapped=False):
    """point_solve_dem(dem, i12s, cohs, dem_std, multilook, samples=1000, stepsize=None):
        Solves a single point.
        dem=scalar: dem height for the point
        i12s=vector: observed subtrrefpha, filtphase,unwrap values for point
        cohs= vector: observed coherence values for point
        dem_std= scalar: estimated dem standard dev. for point
        multilook= scalar: interferogram multilooking
        samples=1000: scalar to be used to constract search space. 
        stepsize=scalar: height sensitivity to use instead of samples to constract search space. 
        
        search space = linspace (dem-3*dem_std , dem+3*dem_std , samples) 
        OR
        search space = r_[dem-3*dem_std : dem+3*dem_std : stepSize]
    """
    import numpy as np
    import os
    os.sys.path.append('/d0/bosmanoglu/projectLocker/pythonUnwrap/trunk')
    import insar
    import scipy
    from scipy import special
    if stepsize is None:
        ss = linspace(dem-3*dem_std , dem+3*dem_std , samples)  #stepsize
    else:
        ss = np.r_[dem-3*dem_std : dem+3*dem_std : stepsize]    
    #convert ss to phase
    sp=np.dot(np.atleast_2d(ss).T, np.atleast_2d(h2phs))        #step phase
    # offset the domain with phase value
    if any(iscomplex(i12s)):
        sp=sp-np.tile(np.angle(i12s), (sp.shape[0],1))
    else:
        sp=sp-np.tile(i12s, (sp.shape[0],1));
    #pdf of dem
    pdem=insar.dem.maximum_likelihood.pdf_dem(dem, ss, dem_std);
    #pdf based on InSAR data
    if figures:
        pint=insar.coh2pdfML( cohs, multilook, domain=sp.T )
        for k in xrange(len(pint)):
            plot(ss, pint[k,:])
        pint=basic.nonan(pint, True).prod(0)
        plot(ss, pdem, 'k--')
        plot(ss, pdem*pint/nanmax(pdem*pint), 'k-.')
        plot(ss, pint/nanmax(pint), 'k:')
        print('i12s/cohs/h2phs')
        print(i12s)
        print(cohs)
        print(h2phs)
    else:
        pint=insar.coh2pdfML( cohs, multilook, domain=sp.T ).prod(0)        
    
    #joint pdf
    jp=pdem*pint
    return ss[jp.argmax()]


def point_solve_int(demminmax, i12s, cohs, h2phs, multilook, samples=1000, stepsize=None, figures=False):
    """point_solve_int(demminmax, i12s, cohs, dem_std, multilook, samples=1000, stepsize=None):
        Solves a single point.
        demminmax=vector: minimum and maximum values for dem.
        i12s=vector: observed subtrrefpha values for point
        cohs= vector: observed coherence values for point
        multilook= scalar: interferogram multilooking
        samples=1000: scalar to be used to constract search space. 
        stepsize=scalar: height sensitivity to use instead of samples to constract search space. 
        
        search space = linspace (demmin , demmax , samples) 
        OR
        search space = r_[demmin : demmax : stepSize]
    """
    import numpy as np
    import os
    os.sys.path.append('/d0/bosmanoglu/projectLocker/pythonUnwrap/trunk')
    import insar
    import scipy
    from scipy import special
    if stepsize is None:
        ss = linspace(min(demminmax) , max(demminmax) , samples)
    else:
        ss = np.r_[min(demminmax) : max(demminmax) : stepsize]
    #convert ss to phase
    sp=np.dot(np.atleast_2d(ss).T, np.atleast_2d(h2phs))
    # offset the domain with phase value
    sp=sp-np.tile(np.angle(i12s), (sp.shape[0],1))
    #pdf of dem
    #pdem=insar.dem.maximum_likelihood.pdf_dem(dem, ss, dem_std);
    #pdf based on InSAR data
    if figures:
        pint=insar.coh2pdfML( cohs, multilook, domain=sp.T )
        for k in xrange(len(pint)):
            plot(ss, pint[k,:])
        pint=pint.prod(0)
        plot(ss, pint/max(pint), 'r:')

    else:
        pint=insar.coh2pdfML( cohs, multilook, domain=sp.T ).prod(0)        
    
    #joint pdf
    #jp=pdem*pint
    jp=pint
    return ss[jp.argmax()]    

def radar_coord_int(demminmax, i12s, cohs, h2phs, ref=None, multilook=1, samples=1000, stepsize=None, study_area=None):
    """radar_coord_dem(dem, i12s, cohs, dem_std=10, ref=None):
    demminmax=vector: minimum and maximum values for dem.
    i12s: [K,M,N]
    cohs: [K,M,N]
    h2phs: [K,M,N]
    dem_std: scalar or [M,N]
    ref: None or tuple (m,n)
    multilook: level of SAR multilooking
    samples=1000, number of samples for search domain
    stepsize= height sensitivity to use instead of samples to constract search space.
    study_area= [m0, mM, n0, nN] 
    """
    i12s=i12s*tile( conj(i12s[:,ref[0],ref[1]]), (i12s.shape[2], i12s.shape[1], 1) ).T   #zero reference
    if study_area is not None:
        i12s = i12s[:, study_area[0]:study_area[1], study_area[2]:study_area[3]]
        cohs = cohs[:, study_area[0]:study_area[1], study_area[2]:study_area[3]]
        h2phs=h2phs[:, study_area[0]:study_area[1], study_area[2]:study_area[3]]
    M=i12s.shape[1];
    N=i12s.shape[2];
    z=zeros([M,N]); #initialize output
        
    t=0;
    for m in xrange(M):
        for n in xrange(N):
            z[m,n]=point_solve_int(demminmax, i12s[:,m,n], cohs[:,m,n], h2phs[:,m,n], multilook, samples=samples, stepsize=stepsize);
        if basic.progresstime(t0=t,timeSpan=30):
            t=basic.time.time()
            basic.progress(p=m,t=M,f="%.3f ")        
    return z    

