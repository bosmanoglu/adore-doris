#!/usr/bin/env python
""" deramp
Calculates a best fitting plane to the phase of the unwrapped interferogram and removes the plane.

Usage: 
 deramp.py -w WIDTH -f FORMAT [-e ESTIMATEFILE] [-o ORDER] FILE

INPUT:
 WIDTH:number of pixels (range samples) for the FILE.
 FORMAT: The format for the input files. DORIS convention is used: r4=real4
 ESTIMATEFILE: This file is subtracted before plane fitting. For unwrapping of 
   SNAPHU topo results it may be possible that the actual topography has a 
   plane. This file is added back to the result before the result is saved.
 ORDER: Degree of the polynomial. Can be 1 or 2. 
 FILE: The unwrapping result file. 
 
EXAMPLES:
 ./deramp.py -w 1189 -f r4 200311_200404.uw
 Writing output to: 200311_200404.uwderamp

 To view the files one can use cpxview.py:
 cpxview.py -w 1189 -f r4 -q normal -c jet -b 200311_200404.uw &
 cpxview.py -w 1189 -f r4 -q normal -c jet -b 200311_200404.uwderamp &
 
DEPENDENCIES:
 python-numpy python-scipy
 To install on ubuntu:
 sudo apt-get install python-numpy python-scipy
 
"""
import sys,os
import getopt
#import adore
#import pylab as mp; #mp=matplotlib.
import numpy as np;
import scipy
scipy.pkgload('optimize')

def usage():
    print __doc__

def fitSurface(x,y,z, weight=None, order=1):
    if weight is not None:
        w=weight;
    else:
        w=np.ones(len(x))
    if order==1:
        fitfunc = lambda p, x, y: p[0]+p[1]*x+p[2]*y
        p0=[0,0.1,0.1] 
    elif order==2:
        fitfunc = lambda p, x, y: p[0]+p[1]*x+p[2]*y+p[3]*x**2+p[4]*y**2+p[5]*x*y
        p0=[0,0.1,0.1,0.1,0.1] 
    else:
        print "order has to be 1 or 2."
        return -1
    errfunc = lambda p, x, y, z, w: w*(fitfunc(p,x,y) - z)
    planefit, success=scipy.optimize.leastsq(errfunc, p0, args=(x,y,z,w))
    return planefit, fitfunc

def derampxyz(x,y,z,weight=None, order=1):
    """derampxyz(x,y,z,weight=None, order=1):
    """
    p,func=fitSurface(x,y,z,weight, order)    
    return z-func(p,x,y);
    
def deramp(inData, estData=None, multilook=[1000,1000], weight=None, order=1):
    X,Y = np.meshgrid(np.r_[0:inData.shape[0]],np.r_[0:inData.shape[1]])
    fitX,fitY=np.meshgrid(np.r_[0:inData.shape[0]:multilook[0]],np.r_[0:inData.shape[1]:multilook[1]])
    #X=X[inData<0.1];
    fitX=fitX.ravel()#[0::multilook[0]]
    #Y=Y[inData<0.1];
    fitY=fitY.ravel()#[0::multilook[1]]
    if estData is not None:
        inData=inData-estData;
    fitData=inData[fitX,fitY]#.ravel()[0::multilook]
    #remove nan values
    ma=np.isnan(fitData)
    if all(ma):
        print "Too many nans. Reduce multilook or remove nans."
        return -1
    if any(ma):
        notNan=~ma
        fitData=fitData[notNan];
        fitX=fitX[notNan];
        fitY=fitY[notNan];
    if weight is not None:
        w=weight[fitX,fitY]
    else:
        w=np.ones(fitX.shape)
    planefit,fitfunc=fitSurface(fitX,fitY,fitData, weight=w, order=order);
    #X,Y = np.meshgrid(np.r_[0:inData.shape[0]],np.r_[0:inData.shape[1]])
    outData=inData-fitfunc(planefit,X.T,Y.T)
    if estData is not None:
        outData=outData+estData
    return outData
    #np.save(fldr+'snaphuDEMdetrended.npy', snaphuDEMdetrended)

def dataFormat2dataType(dataFormat):
    complexFlag=False;
    #### Handle the long format specifier: i.e. complex_real4
    if "real4" in dataFormat:
        datatype="f4"
    elif "short" in dataFormat:
        datatype="i2"
    else:
        datatype=dataFormat

    if "complex" in dataFormat:
        complexFlag=True;
    ### Handle the short format specifier: i.e. cr4    
    if dataFormat=="cr4":
        datatype="f4"        
        complexFlag=True;
    elif dataFormat=="r4":
        datatype="f4"
    elif dataFormat=="ci2":
        datatype="i2"
        complexFlag=True;
    elif  dataFormat=="i2":
        datatype="i2"
    #else: dtype is already set to dataFormat
    return (datatype, complexFlag);    

def getdata(fname, width, dataFormat, length=0):  
    datatype,complexFlag=dataFormat2dataType(dataFormat);
    if complexFlag==True:
        width=2*width;

    if length==0:
        filesize=os.path.getsize(fname)
        length=float(filesize)/width/np.dtype(datatype).itemsize
        if not isint(length):
            print("Error with file width, will continue but results might be bad.")
            print('Width(*2 if complex): %d, Length: %.2f, FileSize: %d' % (width,length,filesize) )
        length=int(length);

    if complexFlag:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
        #data=np.vectorize(complex)(data[:,0:-1:2],data[:,1::2])        
        data=data[:,0:-1:2]+1j*data[:,1::2]
        #data=np.zeros((length,width/2),np.complex);
        #data+=dataP;
    else:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
    return data

def writedata(fname, data, dataFormat):
    datatype,complexFlag=dataFormat2dataType(dataFormat);
    data.astype(np.dtype(datatype)).tofile(fname)
    
def isint(x):
    #http://drj11.wordpress.com/2009/02/27/python-integer-int-float/
    try:
        return int(x) == x
    except:
        return False

def main(argv):
    try:
        inputfile=argv[-1]; 
    except:
        usage()
        sys.exit(2)
        
    argv=argv[0:-1];
    if not os.path.exists(inputfile):
        print "File not found:", inputfile
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "w:f:e:o:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    cfg=dict(opts); #linuxtopia.org/online_books/programming_books/python_programming/python_ch35s03.html
    cfg.setdefault("-f", "cr4")
    cfg.setdefault("-e", "")
    cfg.setdefault("-o", "1")
    cfg["-w"]=int(cfg["-w"])
    cfg["-o"]=int(cfg["-o"]) 
    
    data=getdata(inputfile,cfg["-w"],cfg["-f"])
    if cfg["-e"]:
        eData=getdata(cfg["-e"],cfg["-w"],cfg["-f"])
    else:
        eData=None;
    outData=deramp(data, eData, order=cfg["-o"]);
    print "Writing output to:", inputfile+'deramp'
    writedata(inputfile+'deramp',outData,cfg["-f"]);
    
if __name__ == "__main__":
    main(sys.argv[1:]);    
