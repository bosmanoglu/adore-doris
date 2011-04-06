#!/usr/bin/env python
""" cpxview
Opens complex files using numpy and matplotlib. Functionality and parameters are
similar to cpxfiddle-part of TU-DELFT DORIS software.

Usage: cpxview -w width [-f informat] [-q output] 
	[-e exp] [-s scale] [-l line] [-L line] [-p pixel] [-P pixel]
	[-S x/y] [-M x/y] [-m mirror] [-c file] [-r rmin/rmax] [-B swap] 
	[-H bytes] [-V] [-b] [-h[elp]] inputfile
"""
#
# USAGE: cpxview -w width [-f informat] [-q output] 
#	 [-e exp] [-s scale] [-l line] [-L line] [-p pixel] [-P pixel]
#	 [-S x/y] [-M x/y] [-m mirror] [-c file] [-r rmin/rmax] [-B swap] 
#	 [-H bytes] [-V] [-b] [-h[elp]] inputfile
# DESCRIPTION:
#   Opens complex files using numpy and matplotlib. Functionality and parameters are
#   similar to cpxfiddle-part of TU-DELFT DORIS software.
#
import sys,os
import getopt
import pylab as mp;
import numpy as np;

def usage():
    print __doc__

def main(argv):
    if not argv:
        usage()
        sys.exit(2)
    #inputfile=argv[-1];
    #argv=argv[0:-1];
    try:
        opts, args = getopt.getopt(argv, "w:f:q:e:s:l:L:p:P:S:M:m:c:r:B:H:Vbht")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    inputfile=args[0];
    if not os.path.exists(inputfile):
        print "File not found:", inputfile
        sys.exit(2)
    cfg=dict(opts); #linuxtopia.org/online_books/programming_books/python_programming/python_ch35s03.html
    cfg.setdefault("-f", "cr4")
    cfg.setdefault("-q", "mag")
    cfg.setdefault("-e", 1.)
    cfg.setdefault("-s", 1.)
    cfg.setdefault("-l", 0)
    cfg.setdefault("-L", -1)
    cfg.setdefault("-p", 0)
    cfg.setdefault("-P", -1)
    cfg.setdefault("-S", "1/1")
    cfg.setdefault("-M", "1/1")
    cfg.setdefault("-m", "")
    cfg.setdefault("-c", "gray")
    cfg.setdefault("-r", "0/0")
    cfg.setdefault("-B", "")
    cfg.setdefault("-H", "")
    cfg.setdefault("-b", "")
    cfg["-w"]=int(cfg["-w"]) 
    cfg["-l"]=int(cfg["-l"]) 
    cfg["-L"]=int(cfg["-L"]) 
    cfg["-p"]=int(cfg["-p"]) 
    cfg["-P"]=int(cfg["-P"])
    cfg["Sl"]=int(cfg["-S"].split("/")[0])
    cfg["Sp"]=int(cfg["-S"].split("/")[1])
    cfg["Ml"]=int(cfg["-M"].split("/")[0])
    cfg["Mp"]=int(cfg["-M"].split("/")[1])    
    cfg["-s"]=float(cfg["-s"]) 
    cfg["-e"]=float(cfg["-e"]) 
    cfg["rmin"]=int(cfg["-r"].split("/")[0])
    cfg["rmax"]=int(cfg["-r"].split("/")[1])    
    data=getdata(inputfile,cfg["-w"],cfg["-f"])
    data=data[cfg["-l"]:cfg["-L"]:cfg["Sl"], cfg["-p"]:cfg["-P"]:cfg["Sp"]];
    #multilook
    data=multilook(data, [cfg["Ml"],cfg["Mp"]]);
    if "norm" in cfg["-q"]:
        mp.matshow(cfg["-s"]*data**cfg["-e"]);
    elif "mag" in cfg["-q"]:
        mp.matshow(cfg["-s"]*abs(data)**cfg["-e"])
    elif "pha" in cfg["-q"]:
        mp.matshow(cfg["-s"]*np.angle(data)**cfg["-e"])
    elif "wrap" in cfg["-q"]:
        mp.matshow(cfg["-s"]*wrapToPi(data)**cfg["-e"])
        
    else:
        print "Unknown output type."
        return
    # set colormap
    mp.set_cmap(cfg["-c"])        
    #rescale?
    if cfg["-r"]!="0/0":
        mp.clim([ cfg["rmin"], cfg["rmax"] ]);
    #Place colorbar
    if ("-b", "") in opts:
        mp.colorbar()
    #display file name as title.
    if ("-t", "") in opts:
        mp.title(os.path.basename(inputfile))
    mp.show()

def wrapToPi(x):
    return np.mod(x+np.pi,2*np.pi)-np.pi

def getdata(fname, width, dataFormat, length=0):  
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
        
    if complexFlag==True:
        width=2*width;

    if length==0:
        filesize=os.path.getsize(fname)
        length=float(filesize)/width/np.dtype(datatype).itemsize
        if not isint(length):
            print("Error with file width, will continue but results might be bad.")
            print("Width(*2 if complex): %f, Length: %f, FileSize: %d" ,width,length,filesize)
        length=int(length);

    if complexFlag:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
        data=data[:,0:-1:2]+1j*data[:,1::2]
    else:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
    return data
    
def isint(x):
    #http://drj11.wordpress.com/2009/02/27/python-integer-int-float/
    try:
        return int(x) == x
    except:
        return False

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
    outL=np.floor((L)/ratio[0])
    outP=np.floor((P)/ratio[1])
    x=x[0:ratio[0]*outL,0:ratio[1]*outP]    
    out=x.reshape(outL,ratio[0],outP,ratio[1]);
    return out.mean(axis=3).mean(axis=1);

    
if __name__ == "__main__":
    main(sys.argv[1:]);