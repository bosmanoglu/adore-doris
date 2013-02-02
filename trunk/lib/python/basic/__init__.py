# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:47:54 2010

@author: bosmanoglu

basic library includes several functions to simplify programming.
confirm(prompt=None, resp=False)
ind2sub(shp, idx)
isarray(a)
isint(x)
isfloat(f)
peaks(n=49)
maskshow(array, mask=None)
mdot(listIn)
nonan(array)
progress(p=1,t=1,f="%.3f ")
progresstime(t0=0,timeSpan=120)
rescale(arr, lim)
shallIStop(t0,timeSpan=120)
sub2ind(shap, sub)
tic()
toc(t)
validIndex(arrSize, arrIdx)
wrapToPi(x)
wrapToInt(x, period)
colorbarFigure(cmap,norm,label="")
"""

import operator
import sys
import exceptions
from numpy import *
import pylab as plt
import time
import graphics

class rkdict(dict): #return (missing) key dict
    def __missing__(self, key):
            return key

class DictObj(object):
    def __init__(self, **entries):
        if entries:
            for e in entries:
                #No space and dot for attribute name
                et="_".join(e.split())
                et=et.replace('.','')
                if isinstance(d[e], dict):
                    self.__dict__[et]=DictObj(d[e])
                else:
                    self.__dict__[et]=d[e]              
    def _add_property(self, name, func):
        setattr(self.__class__, name, property(func))        
    def __missing__(self, key):
        return None
            
def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True
    
    Reference:http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation/
    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def corr2(x,y,w):
    '''correlate(x, y, w):
    input is master and slave complex images (tested for 1D only)
    w is the calculation window.
    '''        
    import scipy
    scipy.pkgload('signal')
    
    cor=zeros(size(x))
    corrFilter= ones(w)
    nfilt=corrFilter.size
    corrFilter=corrFilter/nfilt
#    Em=scipy.ndimage.filters.correlate(m*conj(m),corrFilter,mode='nearest')
#    Es=scipy.ndimage.filters.correlate(s*conj(s),corrFilter,mode='nearest')
#    Ems=scipy.ndimage.filters.correlate(m*conj(s),corrFilter,mode='nearest')
    Ex=scipy.signal.signaltools.correlate(x, corrFilter, mode='same')
    Ey=scipy.signal.signaltools.correlate(y, corrFilter, mode='same')
    cor=scipy.signal.signaltools.correlate((x-Ex)*(y-Ey)/sqrt((x-Ex)**2*(y-Ey)**2), corrFilter, mode='same')
    #Vy=scipy.signal.signaltools.correlate((y-Ey)**2, corrFilter, mode='same')
    #cor=abs( (x-Ex)*(y-Ey) / sqrt(Vx*Vy) )
    return cor

def nancorr2(x,y,w):
    '''nancorr2(x, y, w):
    input is master and slave complex images (tested for 1D only)
    w is the calculation window.
    '''        
    import scipy
    scipy.pkgload('signal')
    
    w=array(w);
    cor=zeros(x.shape)
    Ex=empty(x.shape)
    Ey=empty(y.shape)
    for k,l in ( (k,l) for k in range(x.shape[0]) for l in range(x.shape[1]) ):
        idx=[ (kk,ll) for kk in range(k-w[0],k+w[0]) for ll in range(l-w[1], l+w[1]) ]
        vidx=validIndex(x.shape, idx);
        Ex[k,l]=nonan(x[vidx[:,0],vidx[:,1]]).mean()
        Ey[k,l]=nonan(y[vidx[:,0],vidx[:,1]]).mean()
    

    corrFilter= ones(2*w+1)
    nfilt=corrFilter.size
    corrFilter=corrFilter/nfilt
    #Ex=scipy.signal.signaltools.correlate(x, corrFilter, mode='same')
    #Ey=scipy.signal.signaltools.correlate(y, corrFilter, mode='same')
    cor=scipy.signal.signaltools.correlate((x-Ex)*(y-Ey)/sqrt((x-Ex)**2*(y-Ey)**2), corrFilter, mode='same')
    return cor

def cdiff(A, axis=0):
    """cdiff, returns the center difference for Array A in given axis
    """
    singleDim=False
    if len(A.shape)==1:
        A=atleast_2d(A).T
        singleDim=True
    A=rollaxis(A, axis)
    out=zeros(A.shape);    
    out[0,:]=A[0,:]-A[1,:]
    for i in range(1,A.shape[0]-1):
        out[i,:] = (A[i+1,:] - A[i-1,:])/2
    out[-1,:] = A[-1,:]-A[-2,:]
    if singleDim==True:
        return squeeze(rollaxis(out, -axis))
    else:
        return rollaxis(out, -axis)

def div(U,V,spacing=[1.,1.]):
    """div(U,V,spacing=[1.,1.])
    Divergence of a 2D array.
    http://en.wikipedia.org/wiki/Divergence
    """    
    return cdiff(U,0)/spacing[0]+cdiff(V,1)/spacing[1];

def fillNan(arr, copy=True):
    """ outData=basic.fillNan(data, copy=True) 
    
    Fills nan's of an ND-array with a nearest neighbor like algorithm. 
    
    copy: If true creates a copy of the input array and returns it filled. If false
      works on the input array, without creating a copy.
    
    For algorithm details see the authors explanation on the following page.
    Source: http://stackoverflow.com/questions/5551286/filling-gaps-in-a-numpy-array
    """
    # -- setup --
    if copy:
        data=arr.copy()
    else:
        data=arr
    shape = data.shape
    dim = len(shape)
    #data = np.random.random(shape)
    flag = ~isnan(data);#zeros(shape, dtype=bool)
    t_ct = int(data.size/5)
    #flag.flat[random.randint(0, flag.size, t_ct)] = True
    # True flags the data
    # -- end setup --
    
    slcs = [slice(None)]*dim
    
    while any(~flag): # as long as there are any False's in flag
        for i in range(dim): # do each axis
            # make slices to shift view one element along the axis
            slcs1 = slcs[:]
            slcs2 = slcs[:]
            slcs1[i] = slice(0, -1)
            slcs2[i] = slice(1, None)
    
            # replace from the right
            repmask = logical_and(~flag[slcs1], flag[slcs2])
            data[slcs1][repmask] = data[slcs2][repmask]
            flag[slcs1][repmask] = True
    
            # replace from the left
            repmask = logical_and(~flag[slcs2], flag[slcs1])
            data[slcs2][repmask] = data[slcs1][repmask]
            flag[slcs2][repmask] = True

    return data

def ind2sub(shp, idx):
    """ind2sub(shp, idx)
        where shp is shape, and idx is index.
        returns np.unravel_index(idx,shap)
    """
    return unravel_index(idx, shp)
#    '''
#    DO NOT USE NOT CORRECT!!!
#    I1, I2, I3, ..., Idim = ind2sub(shape, idx)
#    Input:
#        shap - shape of the array
#        idx - list of indicies
#    Output:
#        list of subscripts
#    r = array([[0,1,0,0],[0,0,1,1],[1,1,1,0],[1,0,0,1]])
#    l = find(r==1)
#    [cols,rows] = ind2sub(r.shape, l)
#    # The element in coulmn cols[i], and row rows[i] is 1.
#    '''
##    if len(shap) <= dim:
##        shap = shap + tuple(zeros((dim - len(shap),)))
##    else:
##        shap = shap[0:dim-1] + (prod(shap[(dim-1):]),)
#    if not isinstance(idx, ndarray):
#        idx=array(idx)    
#
#    n = len(shap)
#    k = array([1] + cumprod(shap[0:(n-1)]).tolist())
#
#    argout = [zeros((len(idx),))]*n
#
#    for i in xrange(n-1,-1,-1):
#        vi = (idx)%k[-i]
#        vj = (idx-vi)/k[-i]
#        argout[i] = vj
#        idx = vi
#    print argout
#    return argout
        
def isarray(a):
    """
    Test for arrayobjects. Can also handle UserArray instances
    http://mail.python.org/pipermail/matrix-sig/1998-March/002155.html
    """
    try:
        sh = list(a.shape)
    except AttributeError:
        return 0
    try:
        sh[0] = sh[0]+1
        a.shape = sh
    except ValueError:
        return 1
    except IndexError:
        return 1 # ? this is a scalar array
    return 0        

def isint(x):
    #http://drj11.wordpress.com/2009/02/27/python-integer-int-float/
    try:
        return int(x) == x
    except:
        return False

def isfloat(f):
    if not operator.isNumberType(f):
        return 0
    if f % 1:
        return 1
    else:
        return 0
    
def peaks(n=49):
    xx=linspace(-3,3,n)
    yy=linspace(-3,3,n)
    [x,y] = meshgrid(xx,yy)
    z = 3*(1-x)**2*exp(-x**2 - (y+1)**2) \
        - 10*(x/5 - x**3 - y**5)*exp(-x**2-y**2) \
        - 1/3*exp(-(x+1)**2 - y**2)
    return z    

def maskshow(array, mask=None, **kwargs):
    ''' maskshow(array, mask=None)
    Ex: maskshow(kum.topoA[:,:,0], mask<0.5)
    '''
    maskedArray=array.copy();
    if mask != None:          
        maskedArray[mask]=nan;
    return plt.matshow(maskedArray, **kwargs);

def mdot(listIn):
    ''' out=mdot([A,B,C])
    Simulates multiple dot operations.
    Ex: mdot([A,B,C]) is equal to dot(dot(A,B),C)
    '''
    out=listIn[0];
    for k in r_[1:len(listIn)]:
        out=dot(out, listIn[k])
    return out;

def nonan(A, rows=False):
    if rows:
        return A[isnan(A).sum(1)==0];
    else:
        return A[~isnan(A)];    

def nonaninf(A, rows=False):
    m=isnan(A) | isinf(A) 
    if rows:
        return A[m.sum(1)==0];
    else:
        return A[~m];    

def progress(p=1,t=1,f="%.3f "):
    """progress(position=1,totalCount=1)
    display progress in ratio (position/totalCount)
    """
    sys.stdout.write(f % (float(p)/t))
    sys.stdout.flush()
    #print '%.3f' % (float(p)/t) 
    
def progressbar(percentage,interval=10.0,character='.'):
    """progressbar(percentage,interval=10, character='.')
    display progressbar based on the ratio...
    """    
    if percentage%interval == 0:
        sys.stdout.write(str(percentage)+" ")
        sys.stdout.flush()
        
def progresstime(t0=0,timeSpan=30):
    ''' t1=progresstime(t0=0,timeSpan=30)
        Returns True time if currentTime-t0>timeSpan. Otherwise returns False.
    '''
    t1=time.time()
    if t1-t0>timeSpan:
        return True;
    else:
        return False;
        
def rescale(arr, lim, trim=False, arrlim=None):
    """rescale(array, limits, trim=False, arrlim=None)
    scale the values of the array to new limits ([min, max])
    Trim:
      With this option set to a number, the limits are stretced between [mean-TRIM*stdev:mean+TRIM*stdev]
    """
    if arrlim is not None:
        minarr=arrlim[0];
        maxarr=arrlim[1];
    if trim:
        m=arr.mean()
        s=arr.std()
        minarr=m-trim*s;
        maxarr=m+trim*s;
    elif (trim==False) & (arrlim is None):
        minarr=arr.min()
        maxarr=arr.max()
    print [minarr, maxarr]        
    newarr=(arr-minarr)/(maxarr-minarr)*(lim[1]-lim[0])+lim[0]
    newarr[newarr<lim[0]]=lim[0]
    newarr[newarr>lim[1]]=lim[1]
    return newarr
    
def shallIStop(t0,timeSpan=120):
    ''' t1=shallIStop(t0,timeSpan)
    returns time.time() if a long time (timeSpan) has passed since the given
    time (t0). Otherwise returns t0. 
    '''    
    t1=time.time()
    if (t1-t0)>timeSpan:
        if confirm("Shall I stop?", resp=False):
            return 0
        else:
            return t1
    else:
        return t0

def sub2ind(shap, sub):
    """sub2ind(shap, sub):
        Changes a subscript to indices
    """    
    try:
        nSub=size(sub,1);
        for s in xrange(nSub):
            subs=sub[s,]
            for k in xrange(len(shap)):
                if subs[k]<0: raise exceptions.IndexError; # subscript can't be negative
                if (shap[k]-subs[k])<= 0: raise exceptions.IndexError; #subscript can't be bigger than shape        
    except IndexError:
        for k in xrange(len(shap)):
            if sub[k]<0: raise exceptions.IndexError; # subscript can't be negative
            if (shap[k]-sub[k])<= 0: raise exceptions.IndexError; #subscript can't be bigger than shape         
        
    shap=hstack([shap[1:], 1]);
    ind=dot(shap,sub);    
    return ind

def tic():
    ''' returns current time as float
    '''
    return time.time()

def transect(x,y,z,x0,y0,x1,y1,plots=0):
    #convert coord to pixel coord
    d0=sqrt( (x-x0)**2+ (y-y0)**2 );
    i0=d0.argmin();
    x0,y0=unravel_index(i0,x.shape); #overwrite x0,y0
    
    d1=plt.np.sqrt( (x-x1)**2+ (y-y1)**2 );
    i1=d1.argmin();
    x1,y1=unravel_index(i1,x.shape); #overwrite x1,y1    
    #-- Extract the line...    
    # Make a line with "num" points...
    length = int(plt.np.hypot(x1-x0, y1-y0))
    xi, yi = plt.np.linspace(x0, x1, length), plt.np.linspace(y0, y1, length) 
       
    # Extract the values along the line
    #y is the first dimension and x is the second, row,col
    zi = z[xi.astype(plt.np.int), yi.astype(plt.np.int)]
    mz=nonaninf(z.ravel()).mean()
    sz=nonaninf(z.ravel()).std()
    if plots==1:
        plt.matshow(z);plt.clim([mz-2*sz,mz+2*sz]);plt.colorbar();plt.title('transect: (' + str(x0) + ',' + str(y0) + ') (' +str(x1) + ',' +str(y1) + ')' );
        plt.scatter(yi,xi,5,c='r',edgecolors='none')
        plt.figure();plt.scatter(sqrt( (xi-xi[0])**2 + (yi-yi[0])**2 ) , zi)
        #plt.figure();plt.scatter(xi, zi)
        #plt.figure();plt.scatter(yi, zi)

    return (xi, yi, zi);

def toc(t):
    ''' subtracts current time from given, and displays result
    '''
    print time.time()-t, "sec."    
    return

def validIndex(arrSize, arrIdx):
    """validIndex(arrSize, arrIdx):
        Returns validIndex values given the array size. 
    Ex:
        dims=array.shape
        a=0;r=1;
        idx=mgrid[a-1:a+2,r-1:r+2].reshape(2,9)        
        vidx=basic.validIndex(dims, idx.T)
    """    
    if not isinstance(arrSize, ndarray):
        arrSize=array(arrSize)
    if not isinstance(arrIdx, ndarray):
        arrIdx=array(arrIdx)
    arrSize=arrSize-1
    elements=r_[0:arrIdx.shape[0]]
    for k in elements:
        if any((arrSize-arrIdx[k])*arrIdx[k]<0):
            elements[k]=-1
    return arrIdx[elements>-1,]
     
def wrapToPi(x):
    return mod(x+pi,2*pi)-pi   
    
def wrapToInt(x, period):
    return mod(x+period,2*period)-period

def writeToKml(filename, arr2d, NSEW, rotation=0.0, vmin=None, vmax=None, cmap=None, format=None, origin=None, dpi=72):
    """
    writeToKml(filename, arr2d, NSEW, rotation=0.0, vmin=None, vmax=None, cmap=None, format=None, origin=None, dpi=None):
        NSEW=[north, south, east, west]
    """
    import os
    #check if filename has extension
    base,ext=os.path.splitext(filename);
    if len(ext)==0:
        ext='.kml'
    kmlFile=base+ext;
    pngFile=base+'.png';
    f=open(kmlFile,'w');
    f.write('<kml xmlns="http://earth.google.com/kml/2.1">\n')
    f.write('<Document>\n')
    f.write('<GroundOverlay>\n')
    f.write('        <visibility>1</visibility>\n')
    f.write('        <LatLonBox>\n')    
    f.write('                <north>%(#)3.4f</north>\n' % {"#":NSEW[0]})
    f.write('                <south>%(#)3.4f</south>\n'% {"#":NSEW[1]})
    f.write('                <east>%(#)3.4f</east>\n'% {"#":NSEW[2]})
    f.write('                <west>%(#)3.4f</west>\n'% {"#":NSEW[3]})
    f.write('                <rotation>%(#)3.4f</rotation>\n' % {"#":rotation})
    f.write('        </LatLonBox>')
    f.write('        <Icon>')
    f.write('                <href>%(pngFile)s</href>' % {'pngFile':pngFile})
    f.write('        </Icon>')
    f.write('</GroundOverlay>')
    f.write('</Document>')
    f.write('</kml>')
    f.close();
    #Now write the image
    plt.imsave(pngFile, arr2d,vmin=vmin, vmax=vmax, cmap=cmap, format=format, origin=origin, dpi=dpi)
    
def colorbarFigure(cmap,norm,label=""): 
    '''colorbarFigure(cmap,norm,label="")
    basic.colorbarFigure(jet(),normalize(vmin=1,vmax=10),'Label')
    '''
    fig = plt.figure(figsize=(1,5))
    ax1 = fig.add_axes([0.05, 0.1, 0.05, 0.8])
    cb1 = plt.matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap,
                                       norm=norm,
                                       orientation='vertical')
    cb1.set_label(label)
    return fig
    
def findAndReplace(fileList,searchExp,replaceExp):
    """findAndReplace(fileList,searchExp,replaceExp):
    """
    import fileinput
    if not isinstance(fileList, list):
        fileList=[fileList];
    for line in fileinput.input(fileList, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)         

def gridSearch2(fun, bounds,tol=1., goal='min'):
    """gridSearch(fun, args, bounds):
    #for now bounds are actual sampling points (i.e. r_[xmin:xmax])
    Divide and conquer brute-force grid search
    """
    #Main idea is that we want to do only a handful of operations at each time on the multidimensional grid.     
    #Slowly zone in on the lowest score. 
    if goal == 'min':
        fun_z=+inf
        goalfun= lambda x: x<fun_z
    elif goal == 'max':    
        fun_z=-inf
        goalfun= lambda x: x>fun_z
    else:
        fun_z=0
        goalfun=goal
        
    #select spacing
    s=[int(round((max(b)-min(b)))/10.) for b in bounds ]
    for k in xrange(len(s)):
        if s[k]<1:
            s[k]=1
    print s
    #create solution lists
    x=[]
    y=[]
    z=[]
    #start infinite loop
    breakLoop=False
    b0=[]
    while True:
        #create sampling grid
        for k in xrange(len(bounds)):
            b0.append(bounds[k][::s[k]])
        X,Y=meshgrid(b0[0], b0[1])
        print X
        print Y        
        for xy in zip(X.ravel(),Y.ravel()):
            #if (xy[0] in x) and (xy[1] in y):
            if any( (x==xy[0]) & (y==xy[1]) ):
                print [xy[0], xy[1], 0]
                #raise NameError("LogicError")
                continue
            x.append(xy[0])
            y.append(xy[1])            
            z.append(fun(xy))
            if goalfun(z[-1]): # z[-1] < fun_z:
                fun_z=z[-1]
                x0=x[-1];
                y0=y[-1];
                print [99999, x[-1], y[-1], z[-1]]
            else:
                print [x[-1], y[-1], z[-1]]
        #Z=griddata(x,y,z,X,Y); # The first one is actually not necessary
        #set new bounds
        #xy0=Z.argmin()
        #set new bounds
        if breakLoop:
            print "Reached lowest grid resolution."
            break
        if all([sk==1 for sk in s]):
            #Do one more loop then break.
            print "BreakLoop is ON"
            breakLoop=True
        if all(bounds[0]==r_[x0-s[0]:x0+s[0]]) and all(bounds[1]==r_[y0-s[1]:y0+s[1]] ):
            print "Breaking to avoid infinite loop."
            break#if the bounds are the same then break
        bounds[0]=r_[x0-s[0]:x0+s[0]] 
        bounds[1]=r_[y0-s[1]:y0+s[1]] 
        b0=[] #re-initialize              
        #select spacing        
        #s=[max(1,int(round(sk/5.))) for sk in s]
        s=[int(round((max(b)-min(b)))/10.) for b in bounds ]
        for k in xrange(len(s)):
            if s[k]<1:
                s[k]=1
    return [x0,y0,x,y,z]
    
             
