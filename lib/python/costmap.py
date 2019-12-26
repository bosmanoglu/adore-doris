# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 16:18:20 2010

@author: bosmanoglu
"""
from numpy import *
from pylab import *
import basic
import heapq 
import scipy
from scipy import signal, ndimage

def costMapFun(cmap,ref=None,bins=100):
    out=zeros([multiply(*cmap.shape),2]);
    if ref is None:
        ref=basic.ind2sub(cmap.shape,cmap.argmin())
    [distribution, limits]=histogram(cmap[:],bins);
    del distribution
    #iteration start
    pmask=empty((cmap.shape), bool);
    pmask[:]=False;
    pmask[ref]=True;
    lp=-5;lcmin=0;# lp: loop progress, lc:limit counter
    oldprogress=-5;
    qmask=(cmap<limits[lcmin])
    out[0,:]=[ref[0],ref[1]];
    kk=1
    while not all(pmask):
        lc=lcmin;
        mask=scipy.ndimage.morphology.binary_dilation(pmask)        
        mask=logical_xor(mask, pmask); #remove already processed points
        if not any(mask & qmask):
            while lc < bins:
                lc=lc+1
                qmask=(cmap<=limits[lc])
                if sum(qmask)==0: lcmin=lc; #no more high val pixels.
                if any(mask & qmask):                                      
                    break
        mask=(mask & qmask)
        (rA,aA)=where(mask)
        #heapsort fdSum.
        h=[]
        for k in xrange(len(rA)): #idx=index
            idx=(rA[k], aA[k]);
            heapq.heappush(h,(cmap[idx], idx));            
              
        #Now pop que and unwrap
        #for k in xrange(len(rA)):
        while h:
            hpx=heapq.heappop(h);
            out[kk,:]=[hpx[1][0], hpx[1][1]];
            kk=kk+1;
        pmask=(pmask | mask);
        progress=100.0* sum(pmask)/float(product(pmask.shape))
        oldprogress=progress;
        if progress-lp>5:
            lp=progress
            print 'unwrapped  ', len(rA), ' pixels. Total %',  progress, ' lc=', lc
    return out

class costMap:
    '''Cost Map Class '''
    ' REF needs to be (x,y) not [x,y]'
    def __init__(self,cmap,ref=None,bins=100,mask=None):
        self.cmap=cmap;
        if ref is None:
            ref=basic.ind2sub(cmap.shape,cmap.argmin())
        if mask is not None: 
            self.pmask=mask; #Progress Mask
        else:
            self.pmask=empty((cmap.shape), bool);
            self.pmask[:]=False;            
            self.pmask[ref]=True;
        self.hque=[];
        heapq.heappush(self.hque, (cmap[ref], ref)) # add ref to the que. 
        self.startBin=0; #startBin increases as lowcost points finish
        [distribution, self.limits]=histogram(cmap[:],bins);
        self.qmask=(cmap<self.limits[self.startBin]) #startBin=0 #Quality Mask
        #self.enque();
        del distribution;
    def __iter__(self):
        return self
    def next(self):            
        if not self.hque:
            self.enque()
            if not self.hque:
                raise StopIteration
                #return None #return empty list to stop iterator.
        #rraise NameError('debug here')
        return heapq.heappop(self.hque)
        
    def enque(self):
        #repeated attribute lookups (i.e. self.cmap) slow us down.
        #Creating some local variables to eliminate muliple lookups
        #cmap, hque, limits are used in que. 
        lc=self.startBin;
        cmap=self.cmap;
        hque=self.hque;
        limits=self.limits;
        pmask=self.pmask;
        qmask=self.qmask;
        #qmask=(cmap<limits[lc])
        newMask=scipy.ndimage.morphology.binary_dilation(pmask)        
        newMask=logical_xor(newMask, pmask); #remove already processed points
        if not any(newMask & qmask):
            while lc < len(limits)-1:
                lc=lc+1
                qmask=(cmap<=limits[lc])
                if sum(qmask)==0: self.startBin=lc; #no more high val pixels.
                if any(newMask & qmask):
                    self.qmask=qmask                                      
                    break
        newMask=(newMask & qmask)
        (rA,aA)=where(newMask)
        self.pmask=(pmask | newMask) #add newMask to process mask (pmask)
        #heapsort fdSum.
        #self.hque=[]
        for k in xrange(len(rA)): #idx=index
            idx=(rA[k], aA[k]);
            heapq.heappush(hque,(cmap[idx], idx));                

    def push(self, idx, cost=None):
        if cost is None:
            heapq.heappush(self.hque, (self.cmap[idx], idx))
        else:
            heapq.heappush(self.hque, (cost, idx))


def testCostMapClass(cmap):
    cM=costMap(cmap);
    out=zeros([multiply(*cmap.shape),2]);
    k=0;
    t=basic.tic()
    for hpx in cM:
        out[k,:]=[hpx[1][0], hpx[1][1]];
        k=k+1;
        if k % size(cmap,0)==0:
            basic.progress(k, multiply(*cmap.shape), "%.2f ")
    basic.toc(t);
    return out;
    
def testCostMapFun(cmap):
    t=basic.tic()
    out=costMapFun(cmap);
    basic.toc(t);
    return out;

def fisherDistance(m1,s1,mN,sN):
    '''fisherDistance(mean1, std1, meanNeighbors, stdNeighbors):
        Calculates Fisher's Distance based on Osmanoglu et al. 2011, OSA.
    '''
    if not isinstance(mN,ndarray):
        if isinstance(mN,list):
            mN=array(mN)
            sN=array(sN)
        else:
            raise NameError('mN should be list or ndarray')
            
    if any(iscomplex(m1)):
        dm=angle(mN*conj(m1))
    else:
        dm=(m1-mN)
    v1=s1**2;vN=sN**2;
    fd=mean( 0.5*0.5*( \
      (v1+vN)*dm**2.0 / (v1*vN) + \
      log(4.0*pi**2.0*v1*vN) ))            
    return fd

def fisherDistancePoint(m1,s1,mN,sN):
    '''fisherDistancePoint(mean1, std1, mean2, std2):
        fisherDistance=fisherDistancePoint().mean        
    '''
    if not isinstance(mN,ndarray):
        if isinstance(mN,list):
            mN=array(mN)
            sN=array(sN)
        else:
            raise NameError('mN should be list or ndarray')
            
    if any(iscomplex(m1)):
        dm=angle(mN*conj(m1))
    else:
        dm=(m1-mN)
    v1=s1**2;vN=sN**2;
    fd=0.5*0.5*( \
      (v1+vN)*dm**2.0 / (v1*vN) + \
      log(4.0*pi**2.0*v1*vN) )        
    return fd

    
def fisherDistance2(ci,std):
    '''fisherDistance2(complexInterferogram,expectedStandardDeviation)
    Only 2D supported.
    '''
    dims=ci.shape
    fd=zeros(dims)
    for a in xrange(dims[0]): #r_[0:dims[0]]:
        for r in xrange(dims[1]): #r_[0:dims[1]]:
            idx=mgrid[a-1:a+2,r-1:r+2].reshape(2,9)
            #remove center sample
            idx=delete(idx,4,axis=1)
            vidx=basic.validIndex(dims, idx.T)
            m0=0
            mN=angle(ci[vidx[:,0],vidx[:,1]]*conj(ci[a,r]))
            s0=std[a,r]
            sN=std[vidx[:,0],vidx[:,1]]
            fd[a,r]=fisherDistance(m0,s0,mN,sN)                        
    return fd

def fisherDistance2Fast(ci,std):
    '''fisherDistance2Fast2(complexInterferogram,expectedStandardDeviation)
    Only 2D supported.
    '''
    fd=zeros(ci.shape)
    
    fd[0:-1,0:-1]=              fisherDistancePoint(ci[0:-1, 0:-1],std[0:-1, 0:-1],ci[1:  ,1:  ],std[1:  ,1:  ])
    fd[0:-1, :  ]=fd[0:-1, :  ]+fisherDistancePoint(ci[0:-1,  :  ],std[0:-1,  :  ],ci[1:  , :  ],std[1:  , :  ])
    fd[0:-1,1:  ]=fd[0:-1,1:  ]+fisherDistancePoint(ci[0:-1, 1:  ],std[0:-1, 1:  ],ci[1:  ,0:-1],std[1:  ,0:-1])
    fd[ :  ,0:-1]=fd[ :  ,0:-1]+fisherDistancePoint(ci[ :  , 0:-1],std[ :  , 0:-1],ci[ :  ,1:  ],std[ :  ,1:  ])
    fd[ :  ,1:  ]=fd[ :  ,1:  ]+fisherDistancePoint(ci[ :  , 1:  ],std[ :  , 1:  ],ci[ :  ,0:-1],std[ :  ,0:-1])
    fd[1:  ,0:-1]=fd[1:  ,0:-1]+fisherDistancePoint(ci[1:  , 0:-1],std[1:  , 0:-1],ci[0:-1,1:  ],std[0:-1,1:  ])
    fd[1:  ,:   ]=fd[1:  , :  ]+fisherDistancePoint(ci[1:  ,  :  ],std[1:  ,  :  ],ci[0:-1, :  ],std[0:-1, :  ])
    fd[1:  ,1:  ]=fd[1:  ,1:  ]+fisherDistancePoint(ci[1:  , 1:  ],std[1:  , 1:  ],ci[0:-1,0:-1],std[0:-1,0:-1])

    div=ones(ci.shape)*8;
    div[0,:]=5;div[-1,:]=5;div[:,0]=5;div[:,-1]=5;
    div[0,0]=3;div[0,-1]=3;div[-1,-1]=3;div[-1,0]=3;    

    return fd/div;


def graph(arr):
    """ graph(arr)
    calculates and returns graph of the given 2-d array.
    """

    G = {}
    for u in xrange(arr.shape[0]):
        G[u]={}
    for u in xrange(arr.shape[0]):
        for v in xrange(arr.shape[1]):
            G[u][v]=arr[u,v]
            G[v][u]=arr[u,v]
    return G
    
            

    
