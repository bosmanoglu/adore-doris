#!/usr/bin/env python
"""real2cpx
Can be used to create a complex (pixel interleaved) file from two real files.

Usage: 
 real2cpx.py -w WIDTH [-l LENGTH] [-f FORMAT] [-m MAGNITUDE -p PHASE][-r REAL -i IMAGINARY] [-o FORMAT] OUTPUTFILE

 either the -m -p or the -r -i parameters have to be specified. 

INPUT:
 WIDTH:number of pixels (range samples) for the input and output files.
 LENGTH: number of lines (azimuth samples) for the input and output files.
 FORMAT: The format for the input files. DORIS convention is used: r4=real4
         Defaults: -f r4 -o cr4
 MAGNITUDE: A single value or file containing the real values for amplitude.(A of Ae^jp)
 PHASE: A single value or file containing the real values for phase. (p of Ae^jp)
 REAL: A single value or file containing the values for real channel (a of a+ib).
 IMAGINARY: A single value or file containing the values for imaginary channel (b of a+ib). 
 OUTPUTFILE: The complex result file. 
 
EXAMPLES:


 To view the files one can use cpxview.py:
 cpxview.py -w 1189 -f cr4 -q phase -c jet -b  &
 cpxview.py -w 1189 -f cr4 -q mag -c jet -b  &
 
DEPENDENCIES:
 python-numpy python-scipy
 To install on ubuntu:
 sudo apt-get install python-numpy python-scipy
"""

import sys,os
import getopt
import adore
#import pylab as mp; #mp=matplotlib.
import numpy as np;
#import scipy
#scipy.pkgload('optimize')
def usage():
    print __doc__

def main(argv):
    try:
        outputFile=argv[-1]; 
    except:
        usage()
        sys.exit(2)
    argv=argv[0:-1];
    try:
        opts, args = getopt.getopt(argv, "w:l:f:m:p:r:i:o:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    cfg=dict(opts); #linuxtopia.org/online_books/programming_books/python_programming/python_ch35s03.html
    cfg.setdefault("-f", "r4")
    cfg.setdefault("-o", "cr4")
    cfg.setdefault("-l", 0)
    cfg.setdefault("-m", "")
    cfg.setdefault("-p", "")
    cfg.setdefault("-r", "")
    cfg.setdefault("-i", "")    
    w=int(cfg["-w"]) 
    l=int(cfg["-l"]) 

    if cfg["-m"]:
        if os.path.exists(cfg["-m"]):
            mData=adore.getdata(cfg["-m"],w,cfg["-f"])
            if l==0:                
                print "setting L:"+str(mData.shape[0])
                l=mData.shape[0];
        if os.path.exists(cfg["-p"]):
            pData=adore.getdata(cfg["-p"],w,cfg["-f"])
            if l==0:
                print "setting L:"+str(pData.shape[0])
                l=pData.shape[0]
        if not os.path.exists(cfg["-m"]):
            print [cfg["-w"],l]
            mData=float(cfg["-m"])*np.ones([l,w]);
        if not os.path.exists(cfg["-p"]):
            pData=float(cfg["-p"])*np.ones([l,w]);
        print mData.shape 
        print pData.shape            
        outData=mData*np.exp(1j*pData);        
    elif cfg["-r"]:
        if os.path.exists(cfg["-r"]):
            rData=adore.getdata(cfg["-r"],w,cfg["-f"])
            if l==0:                
                l=rData.shape[0]
        if os.path.exists(cfg["-i"]):
            iData=adore.getdata(cfg["-i"],w,cfg["-f"])
            if l==0:
                l=iData.shape[0]
        if not os.path.exists(cfg["-r"]):
            rData=float(cfg["-r"])*np.ones([l,w]);
        if not os.path.exists(cfg["-i"]):
            iData=float(cfg["-i"])*np.ones([l,w]);
        outData=rData+1j*iData;
    bipData=np.empty([outData.shape[0], outData.shape[1]*2]);
    bipData[:,0::2]=outData.real;
    bipData[:,1::2]=outData.imag;
    print "Writing output to:", outputFile
    adore.writedata(outputFile,bipData,cfg["-f"]);
    
if __name__ == "__main__":
    main(sys.argv[1:]);    

