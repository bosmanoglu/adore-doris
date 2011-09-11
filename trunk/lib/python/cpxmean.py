#!/usr/bin/env python
"""cpxmean
Averages multiple complex real float files by complex multiplication. 
Result=cpxmult(C1,C2,...,Cn)^1/n
Usage: 
 cpxmean.py -w WIDTH [-f FORMAT] [-o OUTPUTFILE] complexFile1.cpx complexFile2.cpx [... complexFileN.cpx]

INPUT:
 WIDTH:  number of pixels (range samples) for the input and output files.
 FORMAT: The format for the input files. DORIS convention is used: r4=real4
         Default: -f cr4
 OUTPUTFILE: The complex result file.
         Default: -o cpxmean.out
 
EXAMPLES:


 To view the files one can use cpxview.py:
 cpxview.py -w 1189 -f cr4 -q phase -c jet -b  &
 cpxview.py -w 1189 -f cr4 -q mag -c jet -b  &
 
DEPENDENCIES:
 python-numpy
 To install on ubuntu:
 sudo apt-get install python-numpy
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
        opts, args = getopt.getopt(argv, "w:f:o:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    cfg=dict(opts); #linuxtopia.org/online_books/programming_books/python_programming/python_ch35s03.html
    cfg.setdefault("-f", "cr4")
    cfg.setdefault("-o", "cpxmean.out")
    w=int(cfg["-w"]) 

    outData=None:
    for file in args:
        data=adore.getdata(file,w,cfg["-f"]);
        if any(outData):
            outData=outData * data;
        else:
            outData=data; #first file.
    outData=outData**(1/args.len());
    print "Writing output to:", cfg["-o"]
    adore.writedata(cfg["-o"],outData,cfg["-f"]);
    
if __name__ == "__main__":
    main(sys.argv[1:]);    

