#!/usr/bin/env python
""" cpxview
Opens complex files using numpy and matplotlib. Functionality and parameters are
similar to cpxfiddle-part of TU-DELFT DORIS software.

Usage: cpxview -w width [-f informat] [-q output] [-o outformat]
	[-e exp] [-s scale] [-l line] [-L line] [-p pixel] [-P pixel]
	[-S x/y] [-M x/y] [-m mirror] [-c file] [-r rmin/rmax] [-B] 
	[-b] [-t] [-h] inputfile
	
For longer help message please specify -h. 
"""
#
# USAGE: cpxview -w width [-f informat] [-q output] 
#	 [-e exp] [-s scale] [-l line] [-L line] [-p pixel] [-P pixel]
#	 [-S x/y] [-M x/y] [-m mirror] [-c file] [-r rmin/rmax] [-B] 
#	 [-b] [-h[elp]] inputfile
# DESCRIPTION:
#   Opens complex files using numpy and matplotlib. Functionality and parameters are
#   similar to cpxfiddle-part of TU-DELFT DORIS software.
#
#

import sys,os
import getopt
import pylab as mp;
import numpy as np;

def usage():
    print __doc__

def usageLong():
    print """
  DESCRIPTION [default]:
   -w mandatory      Line length (width, rangepixels, X direction)
   -e [1.0]          Exponent: out=scale*output^exp
   -s [1.0]          Scale     out=scale*output^exp
   -l [1]            First (azimuth Y) line
   -L []             Last (azimuth Y) line (default, all lines)
   -p [1]            First (range X) pixel
   -P []             Last (range X) pixel (default, all pixels)
   -M [1/1]          Multilook factor in X/Y direction (range/azimuth)
                      No subsampling can be used combined with this
                      option. (Multilooking takes complex sum over
                       window(X,Y), divides by number of looks)
                      Output size: [floor(P-p+1)/mlX; floor(L-l+1)/mlY].
   -S [1/1]          Subsample factor in X/Y (range/azimuth)

                      Output dimensionY = ceil((L-l+1)/Y).
                      The last line does not have to equal -L.
                      Output dimensionX = ceil((P-p+1)/X).
                      The last pixel does not have to equal -P.
   -q [mag]          What to output:
                     normal | mag | phase | wrap | real | imag
                      normal    = (real, imag),
                      magnitude = sqrt(real^2 + imag^2),
                      phase     = atan2(imag,real),
                      wrap      = plot wrapped the phase (of unwrapped file)
                      real      = line[2*j],
                      imag      = line[2*j+1].
                     Normal option can be (mis)used to fiddle with, e.g.,
                      float files (though even linelength required?).
   -f [cr4]          Input format identifier:
                     CC1 | CUC1 | CI2 | CI4 | CR4 | CR8
                      for complex 2x1B char, unsigned char, 
                      short integer, integer, float, double
                      (major row order pixel interleaved complex data.)
   -o []             Output format identifier (to stdout):
                      png, pdf, ps, eps and svg.
                      write binary to stdout!
   -c [gray]         Colormap option.
                     gray | jet | hot | cool | hsv
                     autumn | bone | copper | flag | pink
                     prism | spring | summer | winter | spectral
   -m code           Flag to mirror file content in X or Y direction:
                     x | y | xy 
   -r [rmin/rmax]    uses given minimum and maximum range on data as scalling parameters. 
                      Basically, it skips data sampling step for statistics (min,max,mean) computation
                      and defines (min,max,mean) values from given parameters.
                      It only effects magnitude, normal and mixed mode outputs.
                      For example, use it to scale coherence maps to  0-1 range.
                      Tip: no need to use --ignorenan when you are using -r option.
   -B                Swap bytes.
   -b                Add a scalebar.
   -t		     Print file name as figure title. 
   -k [xy|xyz]       Print pixel coordinates(xy) or value (xyz) to stdout on left-click.
   -h                This help.
    """
    
def main(argv):
    if not argv:
        usage()
        sys.exit(2)
    #inputfile=argv[-1];
    #argv=argv[0:-1];
    try:
        opts, args = getopt.getopt(argv, "w:f:q:o:e:s:l:L:p:P:S:M:m:c:r:BH:Vbhtk:v", )
    except getopt.GetoptError:
        print "Unknown option."
        usage()
        sys.exit(2)
    if ("-h", "") in opts:
        usageLong()
        sys.exit(2)
    try:
        inputfile=args[0];
    except:
        print "Input file not specified."
        sys.exit(2)

    for inputfile in args:        
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
        cfg.setdefault("-o", "")
        cfg.setdefault("-k", "xy")
        cfg["-w"]=int(cfg["-w"]) 
        cfg["-l"]=int(cfg["-l"]) 
        cfg["-L"]=int(cfg["-L"]) 
        cfg["-p"]=int(cfg["-p"]) 
        cfg["-P"]=int(cfg["-P"])
        cfg["Sl"]=int(cfg["-S"].split("/")[1])
        cfg["Sp"]=int(cfg["-S"].split("/")[0])
        cfg["Ml"]=int(cfg["-M"].split("/")[1])
        cfg["Mp"]=int(cfg["-M"].split("/")[0])    
        cfg["-s"]=float(cfg["-s"]) 
        cfg["-e"]=float(cfg["-e"]) 
        cfg["rmin"]=int(cfg["-r"].split("/")[0])
        cfg["rmax"]=int(cfg["-r"].split("/")[1])    
        #byteswap on?
        byteSwapFlag=False;
        if ("-B", "") in opts:
            byteSwapFlag=True;
        data=getdata(inputfile,cfg["-w"],cfg["-f"].lower(),0,byteSwapFlag)
        data=data[cfg["-l"]:cfg["-L"]:cfg["Sl"], cfg["-p"]:cfg["-P"]:cfg["Sp"]];
        #multilook
        data=multilook(data, [cfg["Ml"],cfg["Mp"]]);
        # mirror ?
        if "x" in cfg["-m"]:
            data=fliplr(data);
        if "y" in cfg["-m"]:
            data=flipud(data);
        if "norm" in cfg["-q"].lower():
            data=(cfg["-s"]*data**cfg["-e"]);
        elif "mag" in cfg["-q"].lower():
            data=(cfg["-s"]*abs(data)**cfg["-e"])
        elif "pha" in cfg["-q"].lower():
            data=(cfg["-s"]*np.angle(data)**cfg["-e"])
        elif "wrap" in cfg["-q"].lower():
            data=(cfg["-s"]*wrapToPi(data)**cfg["-e"])
        elif "real" in cfg["-q"].lower():
            data=(cfg["-s"]*data.real**cfg["-e"])
        elif "imag" in cfg["-q"].lower():
            data=(cfg["-s"]*data.imag**cfg["-e"])
            
        else:
            print "Unknown output type."
            return
        fg=mp.matshow(data, picker=5);
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
        if cfg["-o"]: #if not empty
            mp.savefig( sys.stdout, format=cfg["-o"])
            ''' if above does not work: http://www.scipy.org/Cookbook/Matplotlib/Using_MatPlotLib_in_a_CGI_script
            pylab.savefig( "tempfile.png", format='png' )
            import shutil
            shutil.copyfileobj(open("tempfile.png",'rb'), sys.stdout)
            #delete tempfile.
            '''
        else:
            if ("-k", "xyz") in opts:
                fg=mp.gcf()
                def onpick(event):
                    ax = mp.gca()
                    inv = ax.transData.inverted()
                    A=inv.transform((event.x,  event.y))
                    try:  
                        v=data[A[1],A[0]]              
                    except:
                        v=np.nan
                    print np.int(np.round(cfg["-l"]+A[1]*cfg["Sl"]*cfg["Ml"])), cfg["-p"]+np.int(np.round(A[0]*cfg["Sp"]*cfg["Mp"])), v
                fg.canvas.mpl_connect('button_press_event', onpick)
            elif ("-k", "xy") in opts:
                fg=mp.gcf()
                def onpick(event):
                    ax = mp.gca()
                    inv = ax.transData.inverted()
                    A=inv.transform((event.x,  event.y))
                    print np.int(np.round(A[1]*cfg["Sl"]*cfg["Ml"])), np.int(np.round(A[0]*cfg["Sp"]*cfg["Mp"]))
                fg.canvas.mpl_connect('button_press_event', onpick)
            mp.show()
    
def wrapToPi(x):
    return np.mod(x+np.pi,2*np.pi)-np.pi

def getdata(fname, width, dataFormat, length=0, byteSwapFlag=False):  
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
        #datatype="f4"
        datatype='complex64'
        complexFlag=False;
    elif dataFormat=="r4":
        datatype="f4"
    if dataFormat=="cr8":
        #datatype="f8"
        datatype='complex128'
        complexFlag=False;
    elif dataFormat=="r8":
        datatype="f8"
    elif dataFormat=="ci2":
        datatype="i2"
        complexFlag=True;
    elif dataFormat=="ci4":
        datatype="i4"
        complexFlag=True;
    elif  dataFormat=="i2":
        datatype="i2"
    elif dataFormat=="cc1":
        datatype="i1"
        complexFlag=True;        
    elif dataFormat=="c1":
        datatype="i1"
    elif dataFormat=="cu1":
        datatype="u1"
        complexFlag=True;                
    elif dataFormat=="u1":
        datatype="u1"
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

#    if complexFlag:
#                 np.dtype((np.int32,{'real':(np.int16, 0),'imag':(np.int16, 2)})
#        datatype=np.dtype( ( {"real":(datatype,0), ("imag", datatype) ] );
    data=np.memmap(fname, dtype=datatype,mode="r", shape=(length,width))
    #data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
    if byteSwapFlag:
        #data=data.byteswap()
        try:
            data.byteswap(True)
        except:
            data=data.byteswap(); #memmap can not be byteswapped in-place.
    if complexFlag: 
        data=data[:,0:-1:2]+1j*data[:,1::2]
#    else:
#        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
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
