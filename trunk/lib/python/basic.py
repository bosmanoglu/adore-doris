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

def maskshow(array, mask=None):
    ''' maskshow(array, mask=None)
    Ex: maskshow(kum.topoA[:,:,0], mask<0.5)
    '''
    maskedArray=array.copy();
    if mask != None:          
        maskedArray[mask]=nan;
    return plt.matshow(maskedArray);

def mdot(listIn):
    ''' out=mdot([A,B,C])
    Simulates multiple dot operations.
    Ex: mdot([A,B,C]) is equal to dot(dot(A,B),C)
    '''
    out=listIn[0];
    for k in r_[1:len(listIn)]:
        out=dot(out, listIn[k])
    return out;

def progress(p=1,t=1,f="%.3f "):
    """progress(position=1,totalCount=1)
    display progress in ratio (position/totalCount)
    """
    sys.stdout.write(f % (float(p)/t))

def progressbar(percentage,interval=10.0,character='.'):
    """progressbar(percentage,interval=10, character='.')
    display progressbar based on the ratio...
    """    
    if percentage%interval == 0:
        sys.stdout.write(str(percentage)+" ")
        
def progresstime(t0=0,timeSpan=120):
    ''' t1=progresstime(t0=0,timeSpan=120)
        Returns True time if currentTime-t0>timeSpan. Otherwise returns False.
    '''
    t1=time.time()
    if t1-t0>timeSpan:
        return True;
    else:
        return False;
        
def rescale(arr, lim):
    """rescale(array, limits)
    scale the values of the array to new limits ([min, max])
    """
    return (arr-arr.min())/(arr.max()-arr.min())*(lim[1]-lim[0])+lim[0];
    
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
    