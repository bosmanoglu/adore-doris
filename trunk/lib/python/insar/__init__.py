# -insar.py- coding: utf-8 -*-
"""
Created on Fri Sep  3 10:46:50 2010

@author: bosmanoglu

InSAR module. Includes functions for analyzing SAR interferometry with python.
"""

from numpy import *
from pylab import *
from basic import *
import scipy
from scipy import ndimage #scipy.pkgload('ndimage')
from scipy import signal #scipy.pkgload('signal') #ndimage
from scipy import interpolate #scipy.pkgload('interpolate'); #interp1d,RectBivariateSpline
from scipy import constants #scipy.pkgload('scipy.constants')
from scipy import optimize #scipy.pkgload('optimize')
from scipy import stats
import time_series

def coh2pdf(coh,n=100):
    domain=linspace(-pi,pi,n);
    pdf=(1-coh**2)/(2*pi) \
        / (1-coh**2 * cos(domain)**2)  \
        * (1 \
        + (coh*cos(domain)*arccos(-1*coh*cos(domain))) \
        / sqrt(1-coh**2*cos(domain)**2) \
          )  
    return pdf

def coh2pdfML(coh,L,n=100,domain=None):
    """coh2pdfML(coh,L,n=100,domain=None)
    coh: scalar or vector. 
    L= scalar, multilook factor
    n=100, number of samples in domain [-pi,pi]
    domain=vector or [#coh, n] . user specified domains. First axis has to be the same as size(coh).
    """
    import scipy
    from scipy import special #scipy.pkgload('special')
    G=scipy.special.gamma #math.gamma #returns the gamma function value at X, same as scipy.special.gamma
    F=scipy.special.hyp2f1 #returns gauss hypergeometric function
    if domain is None:
        domain=linspace(-pi,pi,n);
    if domain.shape[0] == coh.size:
        #user specified domain. Should be the same number of elements with coh:
        #ccd=dot(atleast_2d(coh), atleast_2d(cos(domain)))
        coh=tile(coh, (domain.shape[1],1)).T
        ccd=coh*cos(domain);
    else:
        ccd=dot(atleast_2d(coh).T, atleast_2d(cos(domain)))     #Coherence Cos Domain
        coh=tile(coh, (domain.shape[0],1)).T    
    pdf=(1-coh**2)**L/(2*pi) \
        * F(L, 1, 0.5,ccd**2)  \
        + (G(L+0.5)*(1-coh**2)**L * ccd) \
        / (2*sqrt(pi) * G(L) * (1-ccd**2)**(L+0.5))   
    return pdf


def coh2stdpha(coh,n=100,lut=None):
    '''coh2stdpha(coh,n=100,lut=None)
    n:number of samples between -pi +pi
    lut: number of samples in look-up-table
    ex:
        stdpha=coh2stdpha(coh)
        stdpha=coh2stdpha(coh,lut=100); #This is much faster but only accurate to 1/100th of coh.max()=1 and coh.min()=0. 
    '''
    if isinstance(coh,list):
        coh=array(coh)
    elif isinstance(coh,float):
        coh=array([coh])
    domain=linspace(-pi,pi,n);
    dims=coh.shape
    stdpha=zeros(dims)
    if lut is None:
        for k in xrange(size(coh)):#r_[0:size(coh)]:
                #numpy.trapz(Y,X) = matlab.trapz(X,Y)
                idx=unravel_index(k, dims)
                stdpha[idx]=sqrt(trapz(domain**2*coh2pdf(coh[idx],n),domain));
    else:
        lutx=linspace(coh.min(), coh.max(), lut); #lutx=look up table x
        luty=zeros(lutx.shape); # luty=look up table y
        for k in xrange(len(lutx)):
            luty[k]=sqrt(trapz(domain**2*coh2pdf(lutx[k],n),domain));
        lutf=scipy.interpolate.interp1d(lutx,luty, 'linear')
        stdpha=lutf(coh)
    return stdpha    

def coh2stdphaML(coh,L,n=100,lut=None):
    '''coh2stdpha(coh,L,n=100,lut=None)
    n:number of samples between -pi +pi
    lut: number of samples in look-up-table    
    ex:
        L=iobj.coherence.Multilookfactor_azimuth_direction * iobj.coherence.Multilookfactor_range_direction
        stdpha=coh2stdpha(coh,L)
        stdpha=coh2stdpha(coh,L,lut=100); #This is much faster but only accurate to 1/100th of coh.max()=1 and coh.min()=0. 
    '''
    if isinstance(coh,list):
        coh=array(coh)
    elif isinstance(coh, number):
        coh=array([coh])
    #elif isinstance(coh,float):
    #    coh=array([coh])
    domain=linspace(-pi,pi,n);
    dims=coh.shape
    stdpha=zeros(dims)
    if lut is None:
        for k in xrange(size(coh)):#r_[0:size(coh)]:
                #numpy.trapz(Y,X) = matlab.trapz(X,Y)
                idx=unravel_index(k, dims)
                stdpha[idx]=sqrt(trapz(domain**2*coh2pdfML(coh[idx],L,n),domain));
    else:
        lutx=linspace(coh.min(), coh.max(), lut); #lutx=look up table x
        luty=zeros(lutx.shape); # luty=look up table y
        for k in xrange(len(lutx)):
            luty[k]=sqrt(trapz(domain**2*coh2pdfML(lutx[k],L,n),domain));
        lutf=scipy.interpolate.interp1d(lutx,luty, 'linear')
        stdpha=lutf(coh)
    return stdpha 
    
def coherence(m,s,w):
    '''coherence(master, slave, window):
    input is master and slave complex images (tested for 1D only)
    w is the calculation window.
    '''        
    coh=zeros(size(m))
    corrFilter= ones(w)
    nfilt=corrFilter.size
    corrFilter=corrFilter/nfilt
#    Em=scipy.ndimage.filters.correlate(m*conj(m),corrFilter,mode='nearest')
#    Es=scipy.ndimage.filters.correlate(s*conj(s),corrFilter,mode='nearest')
#    Ems=scipy.ndimage.filters.correlate(m*conj(s),corrFilter,mode='nearest')
    Em=scipy.signal.signaltools.correlate(m*conj(m), corrFilter, mode='same')
    Es=scipy.signal.signaltools.correlate(s*conj(s), corrFilter, mode='same')
    Ems=scipy.signal.signaltools.correlate(m*conj(s), corrFilter, mode='same')
    coh=abs(Ems / 0.5*sqrt(Em**2+Es**2)) #need to divide by two to get root mean square

#    for k in r_[0:len(m)]:
#        if k+w>=len(m):
#            a=k+w-len(m)+1
#        else:
#            a=0
#        mw=m[k-a:k+w]
#        sw=s[k-a:k+w]
#        coh[k]=mean(mw*conj(sw))/sqrt(mean(mw*conj(mw))*mean(sw*conj(sw)))            
    return coh    

def crosscorrelate(m,s):
    """crosscorrelation(m,s):
    """
    coh=zeros(size(m))
    #corrFilter= ones(m.shape)
    #nfilt=corrFilter.size
    #corrFilter=corrFilter/nfilt    
    #m=rescale(m, [-1,1]);
    m=m-m.mean()    
    #s=rescale(s, [-1,1]);
    s=s-s.mean()
    Em=(m**2.).sum()
    Es=(s**2.).sum()
    Ems=(m*s).sum()
    #Em=scipy.signal.signaltools.correlate(m*m, corrFilter, mode='same')
    #Es=scipy.signal.signaltools.correlate(s*s, corrFilter, mode='same')
    #Ems=scipy.signal.signaltools.correlate(m*s, corrFilter, mode='same')
    coh=abs(Ems / sqrt(Em*Es))#1.4142135623730949#(2./sqrt(2.))
    return coh    
    
def correlate(m,s,w):
    coh=zeros(m.shape)
    w0=int(w[0]/2.)
    w1=int(w[1]/2.)
    for k in xrange(m.shape[0]):
        for l in xrange(m.shape[1]):
            if k<w0:                
                kk=r_[0:k+w0];
            elif k>m.shape[0]-w0:
                kk=r_[k-w0:m.shape[0]]
            else:
                kk=r_[k-w0:k+w0]
            if l<w1:                
                ll=r_[0:l+w1];
            elif l>m.shape[1]-w1:
                ll=r_[l-w1:m.shape[1]]
            else:
                ll=r_[l-w1:l+w1]
            K,L=meshgrid(kk,ll)
            coh[k,l]=crosscorrelate(m[K,L],s[K,L])
            #coh[k,l]=abs(scipy.stats.pearsonr(m[K,L].ravel(),s[K,L].ravel())[0]);
    return coh
    
def readComplexData(fname, width, length=0, dtype=float):
    if length==0:
        filesize=os.path.getsize(fname)
        length=float(filesize)/width/2
        if isint(length):
            print("Error with file width, will continue but results might be bad.")
    
    data=fromfile(fname, dtype ,width*2*length).reshape(2*width, length)

def ipd(x):
    return angle(hstack([0, x[1:]*x[0:-1].conj()])).cumsum()

def ipg(cintP, cintNei, unwNei, weiNei=None):
    if weiNei is None:
        weiNei=ones(size(cintNei));        
    return sum(weiNei*(unwNei-angle(cintNei*conj(cintP))))/sum(weiNei);

def radarcode_dem(dem, alpha=0.1745, theta=0.3316, R1=830000., dx=80. ):
    """radarcoded_DEM=radarcode_dem(dem, alpha=0.1745, theta=0.3316, R1=830000., dx=80. )
    calculates a 1m 1rad bperp and runs siminterf without any noise.
    """
    #based on SIMINTERF.m which was 
    # Created by Bert Kampes 05-Oct-2000
    # Tested by Erik Steenbergen
    
    #initialize output
    numlines=dem.shape[0]
    numpixels=dem.shape[1]
    rdem=zeros([numlines,numpixels]);    
    
    # Some variables for ERS1/2 and Envisat
    alpha=deg2rad(10.);      #[rad] baseline orientation
    wavelen = 0.05666;       #[m]   wavelength
    theta = deg2rad(19.)     #[rad] looking angle to first pixel
    R1 = 830000.             #[m]   range to first point
    pi4divlam = (-4.*pi)/wavelen #lam(lambda)=wavelen, can't use lambda in python it is a registered command.
    dx = 80                  #[m]    dem resolution    
    
    #Radarcode DEM by orbit information
    print ('Radarcoding DEM')
    numpixelsdem=dem.shape[1]
    x0=sin(theta) * R1        #x coord. of first DEM point
    sat1_x=0.
    sat1_y=cos(theta) * R1 + dem[1,1]
    maxrange     = sqrt((x0+(numpixelsdem-1)*dx)**2+sat1_y**2)-dem.max();
    R1extra      = R1+dem.max();
    totalrange   = maxrange-R1extra;
    rangebinsize = totalrange/numpixels;
    rangegrid    = arange(R1extra,maxrange,rangebinsize)-rangebinsize;    

    x      = arange(x0,x0+dx*(numpixelsdem),dx);#	x coord. w.r.t. sat1    
    xsqr   = x**2;    
    #compute range for all lines of the dem
    for az in range(0,dem.shape[0]):
        y = sat1_y-dem[az,:]
        range2master = sqrt(y**2+xsqr)
        ## Interpolate p to grid rangebins
        ## range is not always increasing due to foreshortning
        sortindex = argsort(range2master);
        range2master = range2master[sortindex]
        rdem[az,:]=interp(rangegrid,range2master,dem[az,:]);  
    return rdem        
def siminterf(dem,Bperp=100,doNoise=1,waterHeight=None,alpha=0.1745, \
              wavelen=0.05666, theta=0.3316, R1=830000., dx=80.):
    '''[interf,coh,h2ph]=siminterf(dem,Bperp=100,doNoise=1,waterHeight=None,alpha=0.1745, \
              wavelen=0.05666, theta=0.3316, R1=830000, dx=80):
    doNoise can be 1 or 0. If zero gaussian noise is not added.
    '''
    #based on SIMINTERF.m which was 
    # Created by Bert Kampes 05-Oct-2000
    # Tested by Erik Steenbergen
    
    #initialize output
    numlines=dem.shape[0]
    numpixels=dem.shape[1]
    interf=zeros([numlines,numpixels]);
    slope =zeros([numlines,numpixels]);
    h2ph  =ones([numlines,numpixels]);

    # Some variables for ERS1/2 and Envisat
    alpha=deg2rad(10.);      #[rad] baseline orientation
    wavelen = 0.05666;       #[m]   wavelength
    theta = deg2rad(19.)     #[rad] looking angle to first pixel
    R1 = 830000.             #[m]   range to first point
    pi4divlam = (-4.*pi)/wavelen #lam(lambda)=wavelen, can't use lambda in python it is a registered command.
    dx = 80                  #[m]    dem resolution    
    
    #Radarcode DEM by orbit information
    print ('Radarcoding DEM')
    numpixelsdem=dem.shape[1]
    x0=sin(theta) * R1        #x coord. of first DEM point
    sat1_x=0.
    sat1_y=cos(theta) * R1 + dem[1,1]
    maxrange     = sqrt((x0+(numpixelsdem-1)*dx)**2+sat1_y**2)-dem.max();
    R1extra      = R1+dem.max();
    totalrange   = maxrange-R1extra;
    rangebinsize = totalrange/numpixels;
    rangegrid    = arange(R1extra,maxrange,rangebinsize)-rangebinsize;    
    
    #compute range diff to slave satellite
    B =  Bperp / cos(theta-alpha);
    sat2_x = B * cos(alpha);
    sat2_y = B * sin(alpha) + sat1_y;
    x      = arange(x0,x0+dx*(numpixelsdem),dx);#	x coord. w.r.t. sat1
    x2sqr  = (x - sat2_x)**2;
    xsqr   = x**2;    
    #compute range for all lines of the dem
    for az in range(0,dem.shape[0]):
        y = sat1_y-dem[az,:]
        range2master = sqrt(y**2+xsqr)
        y2 = sat2_y-dem[az,:]
        range2slave = sqrt(y2**2+x2sqr)
        phase = pi4divlam * (range2slave-range2master);
        
        # remove reference phase
        tantheta = x/y2
        deltax = dem[az,:] / tantheta # far field approx
        x2_0 = x - deltax
        refpharangemaster = sqrt(sat1_y**2 + x2_0**2)
        refpharangeslave  = sqrt(sat2_y**2 + (x2_0-sat2_x)**2)
        refphase = pi4divlam * (refpharangeslave-refpharangemaster);
        phase = phase - refphase;
        ## Interpolate p to grid rangebins
        ## range is not always increasing due to foreshortning
        sortindex = argsort(range2master);
        range2master = range2master[sortindex]
        phase        = phase[sortindex];         
        interf[az,:]=interp(rangegrid,range2master,phase);  
        
        ## calculate slope and simulate noise
        slopedem= arctan2(diff(dem[az,:]),dx)
        slopedem= hstack((slopedem, [0]))
        slopedem= slopedem[sortindex]
        slope[az,:]=interp(rangegrid,range2master,slopedem);  
        h2ph[az,:] = -pi4divlam*Bperp/(range2master*sin(theta));
    noiseCoherence=simnoise(slope, Bperp)
    noise = noiseCoherence[0];
    coh = noiseCoherence[1];
    if doNoise==1:
        coh=coherence(exp(-1j*interf), exp(-1j*(interf+noise)), [3,3])
        interf= interf + noise        
    if waterHeight!=None:
        waterMask=(dem<waterHeight);
        putmask(interf,waterMask,2*pi*randn(sum(waterMask)));        
        putmask(coh,waterMask,0.05*abs(randn(sum(waterMask))))        
    return [interf,coh,h2ph]

def simnoise(slope,Bperp,Bw=15550000.,wavelen=0.05666, theta=0.3316, R1=830000.):
    """simnoise(slope,Bperp,Bw=15550000.,wavelen=0.05666, theta=0.3316, R1=830000.):
        Bw=range Band width [Hz]
        wavelen = [m]
        theta = look angle [rad]
        R1= range to first pixel [m]
    
    This function calculates the geometric coherence and related noise level
    based on the ERS1/2 configuration (range bandwith, wavelength, look angle,
                                       satellite altitude).
    """
    # Some variables for ERS1/2 and Envisat
    Bw = 15550000;           #[Hz] range bandwidth
    #alpha=deg2rad(10.);      #[rad] baseline orientation
    wavelen = 0.05666;       #[m]   wavelength
    theta = deg2rad(19.)     #[rad] looking angle to first pixel
    R1 = 830000.             #[m]   range to first point
    #pi4divlam = (-4.*pi)/wavelen #lam(lambda)=wavelen, can't use lambda in python it is a registered command.
    #dx = 80                  #[m]    dem resolution
    c = scipy.constants.c;    #[m/s] speed of light
    
    #critical baseline
    Bcritical = wavelen*(Bw/c)*R1*tan(theta-slope);
    gammageom = abs((Bcritical-Bperp)/Bcritical);
    gammageom[isnan(gammageom)]=0
    stdphase=coh2stdpha(gammageom,20)
    #r = random.randn(*gammageom.shape)
    noise = random.randn(*gammageom.shape) * stdphase
    #gammageom = gammageom*(1-gammageom)*abs(r)
    return [noise, gammageom]    

def phaseDerivativeVariance(p):
    """phaseDerivativeVariance(phase)
    
    This function calculates the derivative variance for the given complex phase
    data. This function is based on Bruce Spottiswoode 2008 PhaseDerivativeVariance.m 
    file. This function is re-written based on Ghiglia and Pritt,
    'Two dimensional phase unwrapping', 1998, p.76    
    """
    
    #calculate dr (range)
    dims=p.shape
    dr=zeros(dims)
    #first row
    dr[:,0]=angle(p[:,0]*conj(p[:,1]))
    dr[:,-1]=angle(p[:,-2]*conj(p[:,-1]))
    for r in r_[1:dims[1]-1]:
        dr[:,r]=angle(p[:,r-1]*conj(p[:,r]))
    nfilt=9.0
    corrFilter= array([[1,1,1],[1,1,1],[1,1,1]])/nfilt #http://docs.scipy.org/doc/scipy-0.7.x/reference/tutorial/ndimage.html
    mean_dr=scipy.ndimage.filters.correlate(dr,corrFilter,mode='nearest')
    var_dr=scipy.ndimage.filters.correlate((dr-mean_dr)**2,corrFilter,mode='nearest')
    
    #calculate da (azimuth), dy in spottiswoode
    da=zeros(dims)
    da[0,:]=angle(p[0,:]*conj(p[1,:]))
    da[-1,:]=angle(p[-2,:]*conj(p[-1,:]))
    for a in r_[1:dims[0]-1]:
        da[a,:]=angle(p[a-1,:]*conj(p[a,:]))
    mean_da=scipy.ndimage.filters.correlate(da,corrFilter,mode='nearest')
    var_da=scipy.ndimage.filters.correlate((da-mean_da)**2,corrFilter,mode='nearest')
    var=sqrt(var_da)+sqrt(var_dr)
    return var
    
def phaseDerivativeVarianceReal(p):
    """phaseDerivativeVarianceReal(2dArray)
    
    This function calculates the derivative variance for the given complex phase
    data. This function is based on Bruce Spottiswoode 2008 PhaseDerivativeVariance.m 
    file. This function is re-written based on Ghiglia and Pritt,
    'Two dimensional phase unwrapping', 1998, p.76    
    """
    
    #calculate dr (range)
    dims=p.shape
    dr=np.zeros(dims)
    #first row
    dr[:,0]=p[:,0]-p[:,1]
    dr[:,-1]=p[:,-2]-p[:,-1]
    for r in np.r_[1:dims[1]-1]:
        dr[:,r]=p[:,r-1]-p[:,r]
    nfilt=9.0
    corrFilter=np.array([[1,1,1],[1,1,1],[1,1,1]])/nfilt #http://docs.scipy.org/doc/scipy-0.7.x/reference/tutorial/ndimage.html
    mean_dr=scipy.ndimage.filters.correlate(dr,corrFilter,mode='nearest')
    var_dr=scipy.ndimage.filters.correlate((dr-mean_dr)**2,corrFilter,mode='nearest')
    
    #calculate da (azimuth), dy in spottiswoode
    da=np.zeros(dims)
    da[0,:]=p[0,:]-p[1,:]
    da[-1,:]=p[-2,:]-p[-1,:]
    for a in np.r_[1:dims[0]-1]:
        da[a,:]=p[a-1,:]-p[a,:]
    mean_da=scipy.ndimage.filters.correlate(da,corrFilter,mode='nearest')
    var_da=scipy.ndimage.filters.correlate((da-mean_da)**2,corrFilter,mode='nearest')    
    return np.sqrt(var_da+var_dr)    
    
def cpxgradient(cpx):
    out=[];
    for k in xrange(cpx.ndim):
        cpx=rollaxis(cpx,k,0)
        d=zeros(cpx.shape)
        d[0:-1,:]=angle(cpx[1:,:]*conj(cpx[0:-1,:]))
        d[1:,:]=d[1:,:]+d[0:-1,:]
        d[1:,:]=0.5*d[1:,:]        
        out.append(rollaxis(d,k,0))
    return out;
    
def multilook(x,ratio):
    """multilook(data,ratio)
    data: is a numpy array.
    ratio: is a list of ratios with number of elements equal to number of data dimensions.
    CURRENTLY only 2D data is SUPPORTED.    
    """
    #http://lists.ipython.scipy.org/pipermail/numpy-discussion/2010-July/051760.html
    #l=0;
    L=x.shape[0];
    #p=0;
    P=x.shape[1];
    outL=floor(float(L)/ratio[0])
    outP=floor(float(P)/ratio[1])
    x=x[0:ratio[0]*outL,0:ratio[1]*outP]    
    out=x.reshape(outL,ratio[0],outP,ratio[1]);
    return out.mean(axis=3).mean(axis=1);

def oversample(data,ratio, method='quick', shape=None):
    """oversample(data,ratio, method='quick')
    data: is a numpy array.
    ratio: is a list of ratios with number of elements equal to number of data dimensions.
    CURRENTLY only 2D data is SUPPORTED.    
    """
    includesNan=False   
    if any(np.isnan(data)):     
        m=np.isnan(data);
        z=data.copy();
        z[m]=0;
        includesNan=True
    else:
        z=data    
    x=np.r_[0:z.shape[0]];
    y=np.r_[0:z.shape[1]];
    spl=scipy.interpolate.RectBivariateSpline(x,y,z)
    if shape is None:
        X=np.linspace(0.,z.shape[0]-1,z.shape[0]*ratio[0])
        Y=np.linspace(0.,z.shape[1]-1,z.shape[1]*ratio[1])
    else:
        X=np.linspace(0.,z.shape[0]-1,shape[0])
        Y=np.linspace(0.,z.shape[1]-1,shape[1])
    zo=spl(X,Y);
    if includesNan:
        splm=scipy.interpolate.RectBivariateSpline(x,y,m);
        mo=splm(X,Y)
        mo[mo>0.5]=True
        mo[mo<0.5]=False
        #print  int( np.ceil(np.sqrt(zo.shape[0]/z.shape[0]*zo.shape[1]/z.shape[1])) +3)
        mo=scipy.ndimage.binary_dilation(mo, iterations=int( np.ceil(np.sqrt(zo.shape[0]/z.shape[0]*zo.shape[1]/z.shape[1])) +3) );
        zo[mo.astype(np.bool)]=np.nan
    return zo
    

def rad2dist(radians, wavelength=0.056):
    '''rad2dist(radians, wavelength=0.056)
       Returns distance corresponding to radians in the same unit as wavelegth.
    '''
    return radians*(wavelength/(4*pi));

def dist2rad(distance, wavelength=0.056):
    '''dist2rad(distance, wavelength=0.056):
       Returns radians corresponding to distance. Distance and wavelength has to be in the same units.
    '''
    return distance*4*pi/wavelength

def xyz2los(inVector, projectionVector=zeros([1,3]), incidenceAngle=0, headingAngle=0 ):
    '''xyz2los(inVector, projectionVector=zeros([1,3]), incidenceAngle=0, headingAngle=0 ):
    '''
    if all(projectionVector==0):
        #Using Hanssen Radar Interferometry, page 162 Eq. 5.1.1
        projectionVector=[-sin(incidenceAngle)*cos(headingAngle-1.5*pi), -sin(incidenceAngle)*sin(headingAngle-1.5*pi), cos(incidenceAngle)];#North East Up
    projectionVector=atleast_2d(projectionVector);
    los=dot(inVector, projectionVector.T) / sqrt(nansum((projectionVector)**2));
    return los
