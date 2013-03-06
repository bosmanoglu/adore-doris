# snaphu.py
import _snaphu
import sys, re
import csv
import numpy as np
import adore
import insar

def dict2obj(d):
    #Modified from
    #Ygor Lemos: parand.com/say/index.php/2008/10/13/access-python-dictionary-keys-as-properties/
    class DictObj:
        def __init__(self, **entries):
            for e in entries:
                #No space and dot for attribute name
                et="_".join(e.split())
                et=et.replace('.','')
                if isinstance(d[e], dict):
                    self.__dict__[et]=dict2obj(d[e])
                else:
                    self.__dict__[et]=d[e]                
    return DictObj(**d)

_format =dict(complex_data=1, alt_line_data=3, alt_sample_data=4, float_data=2,
              COMPLEX_DATA=1, ALT_LINE_DATA=3, ALT_SAMPLE_DATA=4, FLOAT_DATA=2)
_cost   =dict(nostatcosts=0, topo=1, defo=2, smooth=3, NOSTATCOSTS=0, TOPO=1, DEFO=2, SMOOTH=3)
_method =dict(mst=1, mcf=2, MST=1, MCF=2)
_transmit=dict(singleanttransmit=1, pingpong=2, repeatpass=1, 
               SINGLEANTTRANSMIT=1, PINGPONG=2, REPEATPASS=1)
_bool   =dict(true=1, false=0, TRUE=1, FALSE=0)
bool    =dict2obj(_bool)
format  =dict2obj(_format)
cost    =dict2obj(_cost)
method  =dict2obj(_method)    
transmit=dict2obj(_transmit)

class _CommentedFile:
  def __init__(self, f, commentstring="#"):
    self.f = f
    self.commentstring = commentstring
  def next(self):
    line = self.f.next()
    while ((not line) or (line=="\n") or line.startswith(self.commentstring)):
      line = self.f.next()
    #print "." + line + "."
    return line
  def __iter__(self):
    return self


class Snaphu(_snaphu._Snaphu):
  def __init__(self):
    self._keyword=dict(INFILE=lambda x: self._infile_set(x),
      LINELENGTH=lambda x: self._lines_set(x),
      OUTFILE=lambda x: self._outfile_set(x),
      WEIGHTFILE=lambda x: self._weightfile_set(x),
      STATCOSTMODE=lambda x: self._costmode_set(_cost[x]),
      CORRFILE=lambda x: self._corrfile_set(x),
      LOGFILE=lambda x: self._logfile_set(x),
      INITMETHOD=lambda x: self._initmethod_set(_method[x]),
      VERBOSE=lambda x: self._verbose_set(_bool[x]),
      INFILEFORMAT=lambda x: self._infileformat_set(_format[x]),
      CORRFILEFORMAT=lambda x: self._corrfileformat_set(_format[x]),
      OUTFILEFORMAT=lambda x: self._outfileformat_set(_format[x]),
      ORBITRADIUS=lambda x: self._orbitradius_set(float(x)),
      EARTHRADIUS=lambda x: self._earthradius_set(float(x)),
      BASELINE=lambda x: self._baseline_set(float(x)),
      BASELINEANGLE_DEG=lambda x: self._baselineangle_set(np.deg2rad(float(x))),
      TRANSMITMODE=lambda x: self._transmitmode_set(_transmit[x]),
      NEARRANGE=lambda x: self._nearrange_set(float(x)),
      DR=lambda x: self._dr_set(float(x)),
      DA=lambda x: self._da_set(float(x)),
      RANGERES=lambda x: self._rangeres_set(float(x)),
      AZRES=lambda x: self._azres_set(float(x)),
      LAMBDA=lambda x: self._wavelength_set(float(x)),
      NLOOKSRANGE=lambda x: self._nlooksrange_set(int(x)),
      NLOOKSAZ=lambda x: self._nlooksaz_set(int(x)),
      NCORRLOOKS=lambda x: self._ncorrlooks_set(float(x)),
      NCORRLOOKSRANGE=lambda x: self._ncorrlooksrange_set(int(x)),
      NCORRLOOKSAZ=lambda x: self._ncorrlooksaz_set(int(x)),
      NTILEROW=lambda x: self._ntilerow_set(int(x)),
      NTILECOL=lambda x: self._ntilecol_set(int(x)),
      ROWOVRLP=lambda x: self._rowovrlp_set(int(x)),
      COLOVRLP=lambda x: self._colovrlp_set(int(x)),
      NPROC=lambda x: self._nthreads_set(int(x)),
      TILECOSTTHRESH=lambda x: self._tilecostthresh_set(int(x)),)
      
    # output file parameters
    self.outfileformat= format.float_data
  
    # input file parameters
    self.infileformat   = format.complex_data
    self.unwrappedinfileformat = format.float_data 
    self.magfileformat  = format.float_data
    self.corrfileformat = format.float_data
    self.ampfileformat  = format.float_data
    self.estfileformat  = format.float_data
    
    # Scattering model parameters #
    self.layminei = 1.25
    self.kds = 0.02
    self.specularexp = 8.0
    self.dzrcritfactor = 2.0
    self.shadow = False #not yet enabled.
    self.dzeimin = -4.0
    self.laywidth = 16
    self.layminei = 1.25
    self.sloperatiofactor = 1.18
    self.sigsqei = 100.0
    
    # Decorrelation model parameters #
    self.drho = 0.005
    self.rhosconst1 = 1.3
    self.rhosconst2 = 0.14
    self.cstd1 = 0.4
    self.cstd2 = 0.35
    self.cstd3 = 0.06
    self.defaultcorr = 0.01
    self.rhominfactor = 1.3
    
    # PDF model parameters #
    self.dzlaypeak = -2.0
    self.azdzfactor = 0.99 
    self.dzeifactor = 4.0
    self.dzeiweight = 0.5
    self.dzlayfactor = 1.0
    self.layconst = 0.9
    self.layfalloffconst = 2.0
    self.sigsqshortmin = 1
    self.sigsqlayfactor = 0.1
    
    # Deformation mode parameters #
    self.defoazdzfactor = 1.0
    self.defothreshfactor = 1.2
    self.defomax = 7.5398
    self.sigsqcorr = 0.05
    self.defolayconst = 0.9
    
    # Algorithm parameters #
    self.eval = False
    self.unwrapped = False
    self.regrowconncomps = False
    self.initonly = False
    self.initmethod = method.mst
    self.costmode = cost.topo
    self.dumpall = False
    self.verbose = True
    self.amplitude = True
    self.havemagnitude = False
    self.flipphasesign = False
    self.initmaxflow = 9999
    self.arcmaxflowconst =3
    self.maxflow = 4
    self.krowei = 65
    self.kcolei = 257
    self.kpardpsi = 7
    self.kperpdpsi = 7
    self.threshold = 0.001
    self.initdzr = 2048.0
    self.initdzstep = 100.0
    self.maxcost = 1000.0
    self.costscale = 100.0
    self.costscaleambight = 80.0
    self.dnomincangle = 0.01
    self.srcrow = 0
    self.srccol = 0
    self.p = 0
    self.nshortcycle = 200
    self.maxnewnodeconst = 0.0008
    self.maxnflowcycles = 10
    self.maxcyclefraction =0.00001
    self.sourcemode = 0
    self.cs2scalefactor = 8
    self.transmitmode = transmit.singleanttransmit
    self.nlooksother = 1
    
    # tiling parameters 
    self.ntilerow = 1
    self.ntilecol = 1
    self.rowovrlp = 0 
    self.colovrlp = 0
    self.piecefirstrow = 1
    self.piecefirstcol = 1
    self.piecenrow = 0 
    self.piecencol = 0
    self.tilecostthresh = 500
    self.minregionsize = 100
    self.nthreads = 1
    self.scndryarcflowmax = 8
    self.tileedgeweight = 2.5
    self.assembleonly = False
    self.rmtmptile = False
    self.tiledir = 'tiles'
     
    # connected component parameters
    self.minconncompfrac = 0.01
    self.conncompthresh = 300
    self.maxncomps = 32

  def read_config(self, configfile):
    tsv_file = csv.reader(_CommentedFile(open(configfile, "rb")), delimiter=' ', skipinitialspace=True)
    for row in tsv_file:
      #print row # prints column 3 of each line
      try: 
        keyword=row[0]
        parameter=row[1]
      except:
        continue
      self._keyword[keyword](parameter)

  def update(self):
    if not self.infile:
      value = raw_input('What is the input file:')
      self._infile_set(value)
    if not self.width>0:
      value = raw_input('What is the file width (i.e. number of pixels in a row):')
      self._width_set(int(value))
    if not self.lines>0:
      value = raw_input('What is the file length (i.e. number of lines):')
      self._lines_set(int(value))
    if (self.ncol<=0 or self.ncol>self.width):
      self.ncol=self.width
    if (self.nrow<=0 or self.nrow>self.lines):
      self.nrow=self.lines
    if (self.piecenrow<=0 or self.piecenrow>self.lines):
      self.piecenrow=self.lines
    if (self.piecencol<=0 or self.piecencol>self.width):
      self.piecencol=self.width

  def unwrap(self):
    # No tile support at the moment
    self.ncol=self.width
    self.nrow=self.lines
    self.piecenrow=self.lines
    self.piecencol=self.width
    self.unwrap_tile()    

  def unwrap_multigrid(self, grids=[2,0]):
    infile=self.infile
    corrfile=self.corrfile
    width=self.width
    lines=self.lines
    outfile=self.outfile
    if not self.estfile:
      estfile='snaphu.est'
    
    cint=adore.getdata(self.infile, self.width, 'cr4')
    coh=adore.getdata(self.corrfile, self.width, 'r4')
    for k in xrange(len(grids)):
      mcint=insar.multilook(cint, [2**grids[k], 2**grids[k]])
      mcoh =insar.multilook(coh , [2**grids[k], 2**grids[k]])
      if k==0:
        self.infile=infile + str(grids[k])
        self.corrfile=corrfile + str(grids[k])
        self.outfile=outfile + str(grids[k])
        adore.writedata(self.infile, mcint, 'cr4')
        adore.writedata(self.corrfile, mcoh, 'r4')
        self.width=mcint.shape[1]
        self.lines=mcint.shape[0]
        self.update()
        self.unwrap_tile()
      else:
        munw=adore.getdata(self.outfile, self.width, 'r4')    
        if grids[k]==0:
          unwk=insar.oversample(munw, [1,1], shape=(lines, width))
          self.outfile=outfile
          self.infile=infile
          self.width=width
          self.lines=lines
          self.corrfile=corrfile
        self.estfile=estfile + str(grids[k-1])     
        adore.writedata(self.estfile, unwk, 'r4')
        self.estfileformat=format.float_data
        self.update()
        self.unwrap()
          
    
