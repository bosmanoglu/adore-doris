# file: _snaphu.pyx

import numpy as np
cimport numpy as np
from libc.stdlib cimport malloc, free

cdef extern from "string.h":
    char *strcpy(char *dest, char *src)
    char *strncpy(char *dest, char *src, size_t n)

cdef extern from "snaphu_cs2types.h":
    pass


cdef extern from "snaphu.h":
    # /* run-time parameter data structure */
    #int MAXSTRLEN         # 512
    ctypedef char maxstrchar[512] 
    #ctypedef char *maxstrchar=<char *>malloc(512);    
    ctypedef struct paramT:
        # /* SAR and geometry parameters */
        double orbitradius     # /* radius of platform orbit (meters) */
        double altitude        # /* SAR altitude (meters) */
        double earthradius     # /* radius of earth (meters) */
        double bperp           # /* nominal perpendiuclar baseline (meters) */
        signed char transmitmode # /* transmit mode (PINGPONG or SINGLEANTTRANSMIT) */
        double baseline        # /* baseline length (meters, always postive) */
        double baselineangle   # /* baseline angle above horizontal (rad) */
        long nlooksrange       # /* number of looks in range for input data */ 
        long nlooksaz          # /* number of looks in azimuth for input data */ 
        long nlooksother       # /* number of nonspatial looks for input data */ 
        double ncorrlooks      # /* number of independent looks in correlation est */
        long ncorrlooksrange   # /* number of looks in range for correlation */ 
        long ncorrlooksaz      # /* number of looks in azimuth for correlation */ 
        double nearrange       # /* slant range to near part of swath (meters) */
        double dr              # /* range bin spacing (meters) */
        double da              # /* azimuth bin spacing (meters) */
        double rangeres        # /* range resolution (meters) */
        double azres           # /* azimuth resolution (meters) */
        double wavelength      # /* wavelength (meters) */
          # /* scattering model parameters */
        double kds             # /* ratio of diffuse to specular scattering */
        double specularexp     # /* power specular scattering component */
        double dzrcritfactor   # /* fudge factor for linearizing scattering model */
        signed char shadow     # /* allow discontinuities from shadowing */
        double dzeimin         # /* lower limit for backslopes (if shadow = FALSE) */
        long laywidth          # /* width of window for summing layover brightness */
        double layminei        # /* threshold brightness for assuming layover */
        double sloperatiofactor# /* fudge factor for linearized scattering slopes */
        double sigsqei         # /* variance (dz, meters) due to uncertainty in EI */
          # /* decorrelation model parameters */
        double drho            # /* step size of correlation-slope lookup table */
        double rhosconst1,rhosconst2# /* for calculating rho0 in biased rho */
        double cstd1,cstd2,cstd3# /* for calculating correlation power given nlooks */
        double defaultcorr     # /* default correlation if no correlation file */
        double rhominfactor    # /* threshold for setting unbiased correlation to 0 */
         # /* pdf model parameters */
        double dzlaypeak       # /* range pdf peak for no discontinuity when bright */
        double azdzfactor      # /* fraction of dz in azimuth vs. rnage */
        double dzeifactor      # /* nonlayover dz scale factor */
        double dzeiweight      # /* weight to give dz expected from intensity */
        double dzlayfactor     # /* layover regime dz scale factor */
        double layconst        # /* normalized constant pdf of layover edge */
        double layfalloffconst # /* factor of sigsq for layover cost increase */
        long sigsqshortmin     # /* min short value for costT variance */
        double sigsqlayfactor  # /* fration of ambiguityheight^2 for layover sigma */

          # /* deformation mode parameters */
        double defoazdzfactor  # /* scale for azimuth ledge in defo cost function */
        double defothreshfactor# /* factor of rho0 for discontinuity threshold */
        double defomax         # /* max discontinuity (cycles) from deformation */
        double sigsqcorr       # /* variance in measured correlation */
        double defolayconst    # /* layconst for deformation mode */

        # /* algorithm parameters */
        signed char eval     # /* evaluate unwrapped input file if TRUE */
        signed char unwrapped  # /* input file is unwrapped if TRUE */
        signed char regrowconncomps# /* grow connected components and exit if TRUE */
        signed char initonly   # /* exit after initialization if TRUE */
        signed char initmethod # /* MST or MCF initialization */
        signed char costmode   # /* statistical cost mode */
        signed char dumpall    # /* dump intermediate files */
        signed char verbose    # /* print verbose output */
        signed char amplitude  # /* intensity data is amplitude, not power */
        signed char havemagnitude # /* flag to create correlation from other inputs */
        signed char flipphasesign # /* flag to flip phase and flow array signs */
        long initmaxflow       # /* maximum flow for initialization */
        long arcmaxflowconst   # /* units of flow past dzmax to use for initmaxflow */
        long maxflow           # /* max flow for tree solve looping */
        long krowei, kcolei    # /* size of boxcar averaging window for mean ei */
        long kpardpsi          # /* length of boxcar for mean wrapped gradient */
        long kperpdpsi         # /* width of boxcar for mean wrapped gradient */
        double threshold       # /* thershold for numerical dzrcrit calculation */
        double initdzr         # /* initial dzr for numerical dzrcrit calc. (m) */
        double initdzstep      # /* initial stepsize for spatial decor slope calc. */
        double maxcost         # /* min and max float values for cost arrays */
        double costscale       # /* scale factor for discretizing to integer costs */
        double costscaleambight# /* ambiguity height for auto costs caling */
        double dnomincangle    # /* step size for range-varying param lookup table */
        long srcrow,srccol     # /* source node location */
        double p               # /* power for Lp-norm solution (less than 0 is MAP) */
        long nshortcycle       # /* number of points for one cycle in short int dz */
        double maxnewnodeconst # /* number of nodes added to tree on each iteration */
        long maxnflowcycles    # /* max number of cycles to consider nflow done */
        double maxcyclefraction# /* ratio of max cycles to pixels */
        long sourcemode        # /* 0, -1, or 1, determines how tree root is chosen */
        long cs2scalefactor    # /* scale factor for cs2 initialization (eg, 3-30) */
        # /* tiling parameters */
        long ntilerow          # /* number of tiles in azimuth */
        long ntilecol          # /* number of tiles in range */
        long rowovrlp          # /* pixels of overlap between row tiles */
        long colovrlp          # /* pixels of overlap between column tiles */
        long piecefirstrow     # /* first row (indexed from 1) for piece mode */
        long piecefirstcol     # /* first column (indexed from 1) for piece mode */
        long piecenrow         # /* number of rows for piece mode */
        long piecencol         # /* number of rows for piece mode */
        long tilecostthresh    # /* maximum cost within single reliable tile region */
        long minregionsize     # /* minimum number of pixels in a region */
        long nthreads          # /* number of parallel processes to run */
        long scndryarcflowmax  # /* max flow increment for which to keep cost data */
        double tileedgeweight  # /* weight applied to tile-edge secondary arc costs */
        signed char assembleonly # /* flag for assemble-only (no unwrap) mode */
        signed char rmtmptile  # /* flag for removing temporary tile files */
        char *tiledir     # /* directory for temporary tile files */

        # /* connected component parameters */
        double minconncompfrac # /* min fraction of pixels in connected component */
        long conncompthresh    # /* cost threshold for connected component */
        long maxncomps         # /* max number of connected components */

    # /* input file name data structure */
    ctypedef struct infileT:
        char *infile             # /* input interferogram */
        char *magfile            # /* interferogram magnitude (optional) */
        char *ampfile            # /* image amplitude or power file */
        char *ampfile2           # /* second amplitude or power file */
        char *weightfile         # /* arc weights */
        char *corrfile           # /* correlation file */
        char *estfile            # /* unwrapped estimate */
        char *costinfile         # /* file from which cost data is read */
        signed char infileformat           # /* input file format */
        signed char unwrappedinfileformat  # /* input file format if unwrapped */
        signed char magfileformat          # /* interferogram magnitude file format */
        signed char corrfileformat         # /* correlation file format */
        signed char weightfileformat       # /* weight file format */
        signed char ampfileformat          # /* amplitude file format */
        signed char estfileformat          # /* unwrapped-estimate file format */

    # /* output file name data structure */
    ctypedef struct outfileT:
        char *outfile            # /* unwrapped output */
        char *initfile           # /* unwrapped initialization */
        char *flowfile           # /* flows of unwrapped solution */
        char *eifile             # /* despckled, normalized intensity */
        char *rowcostfile        # /* statistical azimuth cost array */
        char *colcostfile        # /* statistical range cost array */
        char *mstrowcostfile     # /* scalar initialization azimuth costs */
        char *mstcolcostfile     # /* scalar initialization range costs */
        char *mstcostsfile       # /* scalar initialization costs (all) */
        char *corrdumpfile       # /* correlation coefficient magnitude */
        char *rawcorrdumpfile    # /* correlation coefficient magnitude */
        char *conncompfile       # /* connected component map or mask */
        char *costoutfile        # /* file to which cost data is written */
        char *logfile            # /* file to which parmeters are logged */
        signed char outfileformat          # /* output file format */

    # /* tile parameter data structure */
    ctypedef struct tileparamT:
        long firstcol          # /* first column of tile to process (index from 0) */
        long ncol              # /* number of columns in tile to process */
        long firstrow          # /* first row of tile to process (index from 0) */
        long nrow              # /* number of rows in tile to process */

    #ctypedef outfileT outfileST
    #ctypedef infileT infileST
    #ctypedef paramT paramST
    #ctypedef tileparamT tileparamST

    cdef void UnwrapTile(infileT *infiles, outfileT *outfiles, paramT *params, tileparamT *tileparams, long, long) except *
    cdef void SetStreamPointers() except *
    cdef void CheckParams(infileT *infiles, outfileT *outfiles, long, long, paramT *params) except *

cdef class _Snaphu:
    cdef tileparamT tP
    cdef paramT pP
    cdef infileT iP
    cdef outfileT oP
    cdef np.dict formats
    cdef np.dict method
    cdef np.dict algorithm
    cdef np.dict transmit
    cdef np.dict inp
    cdef np.dict out
    cdef np.dict param
    cpdef np.dict tile
    cdef np.long nlines
    cdef np.long nwidth
   
    def _lines_get(self):
        return self.nlines
    def _lines_set(self, value):
        self.nlines=<np.long> value
    lines=property(_lines_get, _lines_set)

    def _width_get(self):
        return self.nwidth
    def _width_set(self, value):
        self.nwidth= <np.long> value
    width=property(_width_get, _width_set)

    def _firstcol_get(self):
        return self.tP.firstcol
    def _firstcol_set(self, value):
        self.tP.firstcol=<np.long> value
    firstcol=property(_firstcol_get, _firstcol_set)

    def _ncol_get(self):
        return self.tP.ncol
    def _ncol_set(self, value):
        self.tP.ncol=<np.long> value
    ncol=property(_ncol_get, _ncol_set)

    def _firstrow_get(self):
        return self.tP.firstrow
    def _firstrow_set(self, value):
        self.tP.firstrow=<np.long> value
    firstrow=property(_firstrow_get, _firstrow_set)

    def _nrow_get(self):
        return self.tP.nrow
    def _nrow_set(self, value):
        self.tP.nrow=<np.long> value
    nrow=property(_nrow_get, _nrow_set)

    def _outfile_get(self):
        return self.oP.outfile
    def _outfile_set(self, value):
        strcpy(self.oP.outfile, value)
    outfile=property(_outfile_get, _outfile_set)

    def _initfile_get(self):
        return self.oP.initfile
    def _initfile_set(self, value):
        strcpy(self.oP.initfile, value)
    initfile=property(_initfile_get, _initfile_set)

    def _flowfile_get(self):
        return self.oP.flowfile
    def _flowfile_set(self, value):
        strcpy(self.oP.flowfile, value)
    flowfile=property(_flowfile_get, _flowfile_set)

    def _eifile_get(self):
        return self.oP.eifile
    def _eifile_set(self, value):
        strcpy(self.oP.eifile, value)
    eifile=property(_eifile_get, _eifile_set)

    def _rowcostfile_get(self):
        return self.oP.rowcostfile
    def _rowcostfile_set(self, value):
        strcpy(self.oP.rowcostfile, value)
    rowcostfile=property(_rowcostfile_get, _rowcostfile_set)

    def _colcostfile_get(self):
        return self.oP.colcostfile
    def _colcostfile_set(self, value):
        strcpy(self.oP.colcostfile, value)
    colcostfile=property(_colcostfile_get, _colcostfile_set)

    def _mstrowcostfile_get(self):
        return self.oP.mstrowcostfile
    def _mstrowcostfile_set(self, value):
        strcpy(self.oP.mstrowcostfile, value)
    mstrowcostfile=property(_mstrowcostfile_get, _mstrowcostfile_set)

    def _mstcolcostfile_get(self):
        return self.oP.mstcolcostfile
    def _mstcolcostfile_set(self, value):
        strcpy(self.oP.mstcolcostfile, value)
    mstcolcostfile=property(_mstcolcostfile_get, _mstcolcostfile_set)

    def _mstcostsfile_get(self):
        return self.oP.mstcostsfile
    def _mstcostsfile_set(self, value):
        strcpy(self.oP.mstcostsfile, value)
    mstcostsfile=property(_mstcostsfile_get, _mstcostsfile_set)

    def _rawcorrdumpfile_get(self):
        return self.oP.rawcorrdumpfile
    def _rawcorrdumpfile_set(self, value):
        strcpy(self.oP.rawcorrdumpfile, value)
    rawcorrdumpfile=property(_rawcorrdumpfile_get, _rawcorrdumpfile_set)

    def _corrdumpfile_get(self):
        return self.oP.corrdumpfile
    def _corrdumpfile_set(self, value):
        strcpy(self.oP.corrdumpfile, value)
    corrdumpfile=property(_corrdumpfile_get, _corrdumpfile_set)

    def _conncompfile_get(self):
        return self.oP.conncompfile
    def _conncompfile_set(self, value):
        strcpy(self.oP.conncompfile, value)
    conncompfile=property(_conncompfile_get, _conncompfile_set)

    def _logfile_get(self):
        return self.oP.logfile
    def _logfile_set(self, value):
        strcpy(self.oP.logfile, value)
    logfile=property(_logfile_get, _logfile_set)

    def _costoutfile_get(self):
        return self.oP.costoutfile
    def _costoutfile_set(self, value):
        strcpy(self.oP.costoutfile, value)
    costoutfile=property(_costoutfile_get, _costoutfile_set)

    def _outfileformat_get(self):
        return self.oP.outfileformat
    def _outfileformat_set(self, value):
        self.oP.outfileformat= value
    outfileformat=property(_outfileformat_get, _outfileformat_set)

    def _infile_get(self):
        return self.iP.infile
    def _infile_set(self, value):
        strcpy(self.iP.infile, value) 
    infile=property(_infile_get, _infile_set)

    def _magfile_get(self):
        return self.iP.magfile
    def _magfile_set(self, value):
        strcpy(self.iP.magfile, value)
    magfile=property(_magfile_get, _magfile_set)

    def _ampfile_get(self):
        return self.iP.ampfile
    def _ampfile_set(self, value):
        strcpy(self.iP.ampfile, value)
    ampfile=property(_ampfile_get, _ampfile_set)

    def _ampfile2_get(self):
        return self.iP.ampfile2
    def _ampfile2_set(self, value):
        strcpy(self.iP.ampfile2, value)
    ampfile2=property(_ampfile2_get, _ampfile2_set)

    def _weightfile_get(self):
        return self.iP.weightfile
    def _weightfile_set(self, value):
        strcpy(self.iP.weightfile, value)
    weightfile=property(_weightfile_get, _weightfile_set)

    def _corrfile_get(self):
        return self.iP.corrfile
    def _corrfile_set(self, value):
        strcpy(self.iP.corrfile, value)
    corrfile=property(_corrfile_get, _corrfile_set)

    def _estfile_get(self):
        return self.iP.estfile
    def _estfile_set(self, value):
        strcpy(self.iP.estfile, value)
    estfile=property(_estfile_get, _estfile_set)

    def _costinfile_get(self):
        return self.iP.costinfile
    def _costinfile_set(self, value):
        strcpy(self.iP.costinfile, value)
    costinfile=property(_costinfile_get, _costinfile_set)

    def _infileformat_get(self):
        return self.iP.infileformat
    def _infileformat_set(self, value):
        self.iP.infileformat= value
    infileformat=property(_infileformat_get, _infileformat_set)

    def _unwrappedinfileformat_get(self):
        return self.iP.unwrappedinfileformat
    def _unwrappedinfileformat_set(self, value):
        self.iP.unwrappedinfileformat= value
    unwrappedinfileformat=property(_unwrappedinfileformat_get, _unwrappedinfileformat_set)

    def _magfileformat_get(self):
        return self.iP.magfileformat
    def _magfileformat_set(self, value):
        self.iP.magfileformat= value
    magfileformat=property(_magfileformat_get, _magfileformat_set)

    def _corrfileformat_get(self):
        return self.iP.corrfileformat
    def _corrfileformat_set(self, value):
        self.iP.corrfileformat= value
    corrfileformat=property(_corrfileformat_get, _corrfileformat_set)

    def _ampfileformat_get(self):
        return self.iP.ampfileformat
    def _ampfileformat_set(self, value):
        self.iP.ampfileformat= value
    ampfileformat=property(_ampfileformat_get, _ampfileformat_set)

    def _estfileformat_get(self):
        return self.iP.estfileformat
    def _estfileformat_set(self, value):
        self.iP.estfileformat= value
    estfileformat=property(_estfileformat_get, _estfileformat_set)

    def _orbitradius_get(self):
        return self.pP.orbitradius
    def _orbitradius_set(self, value):
        self.pP.orbitradius= value
    orbitradius=property(_orbitradius_get, _orbitradius_set)

    def _altitude_get(self):
        return self.pP.altitude
    def _altitude_set(self, value):
        self.pP.altitude= value
    altitude=property(_altitude_get, _altitude_set)

    def _earthradius_get(self):
        return self.pP.earthradius
    def _earthradius_set(self, value):
        self.pP.earthradius= value
    earthradius=property(_earthradius_get, _earthradius_set)

    def _bperp_get(self):
        return self.pP.bperp
    def _bperp_set(self, value):
        self.pP.bperp= value
    bperp=property(_bperp_get, _bperp_set)

    def _transmitmode_get(self):
        return self.pP.transmitmode
    def _transmitmode_set(self, value):
        self.pP.transmitmode= value
    transmitmode=property(_transmitmode_get, _transmitmode_set)

    def _baseline_get(self):
        return self.pP.baseline
    def _baseline_set(self, value):
        self.pP.baseline= value
    baseline=property(_baseline_get, _baseline_set)

    def _baselineangle_get(self):
        return self.pP.baselineangle
    def _baselineangle_set(self, value):
        self.pP.baselineangle= value
    baselineangle=property(_baselineangle_get, _baselineangle_set)

    def _nlooksrange_get(self):
        return self.pP.nlooksrange
    def _nlooksrange_set(self, value):
        self.pP.nlooksrange= value
    nlooksrange=property(_nlooksrange_get, _nlooksrange_set)

    def _nlooksaz_get(self):
        return self.pP.nlooksaz
    def _nlooksaz_set(self, value):
        self.pP.nlooksaz= value
    nlooksaz=property(_nlooksaz_get, _nlooksaz_set)

    def _nlooksother_get(self):
        return self.pP.nlooksother
    def _nlooksother_set(self, value):
        self.pP.nlooksother= value
    nlooksother=property(_nlooksother_get, _nlooksother_set)

    def _ncorrlooks_get(self):
        return self.pP.ncorrlooks
    def _ncorrlooks_set(self, value):
        self.pP.ncorrlooks= value
    ncorrlooks=property(_ncorrlooks_get, _ncorrlooks_set)

    def _ncorrlooksrange_get(self):
        return self.pP.ncorrlooksrange
    def _ncorrlooksrange_set(self, value):
        self.pP.ncorrlooksrange= value
    ncorrlooksrange=property(_ncorrlooksrange_get, _ncorrlooksrange_set)

    def _ncorrlooksaz_get(self):
        return self.pP.ncorrlooksaz
    def _ncorrlooksaz_set(self, value):
        self.pP.ncorrlooksaz= value
    ncorrlooksaz=property(_ncorrlooksaz_get, _ncorrlooksaz_set)

    def _nearrange_get(self):
        return self.pP.nearrange
    def _nearrange_set(self, value):
        self.pP.nearrange= value
    nearrange=property(_nearrange_get, _nearrange_set)

    def _dr_get(self):
        return self.pP.dr
    def _dr_set(self, value):
        self.pP.dr= value
    dr=property(_dr_get, _dr_set)

    def _da_get(self):
        return self.pP.da
    def _da_set(self, value):
        self.pP.da= value
    da=property(_da_get, _da_set)

    def _rangeres_get(self):
        return self.pP.rangeres
    def _rangeres_set(self, value):
        self.pP.rangeres= value
    rangeres=property(_rangeres_get, _rangeres_set)

    def _azres_get(self):
        return self.pP.azres
    def _azres_set(self, value):
        self.pP.azres= value
    azres=property(_azres_get, _azres_set)

    def _wavelength_get(self):
        return self.pP.wavelength
    def _wavelength_set(self, value):
        self.pP.wavelength= value
    wavelength=property(_wavelength_get, _wavelength_set)

    def _kds_get(self):
        return self.pP.kds
    def _kds_set(self, value):
        self.pP.kds= value
    kds=property(_kds_get, _kds_set)

    def _specularexp_get(self):
        return self.pP.specularexp
    def _specularexp_set(self, value):
        self.pP.specularexp= value
    specularexp=property(_specularexp_get, _specularexp_set)

    def _dzrcritfactor_get(self):
        return self.pP.dzrcritfactor
    def _dzrcritfactor_set(self, value):
        self.pP.dzrcritfactor= value
    dzrcritfactor=property(_dzrcritfactor_get, _dzrcritfactor_set)

    def _shadow_get(self):
        return self.pP.shadow
    def _shadow_set(self, value):
        self.pP.shadow= value
    shadow=property(_shadow_get, _shadow_set)

    def _dzeimin_get(self):
        return self.pP.dzeimin
    def _dzeimin_set(self, value):
        self.pP.dzeimin= value
    dzeimin=property(_dzeimin_get, _dzeimin_set)

    def _laywidth_get(self):
        return self.pP.laywidth
    def _laywidth_set(self, value):
        self.pP.laywidth= value
    laywidth=property(_laywidth_get, _laywidth_set)

    def _layminei_get(self):
        return self.pP.layminei
    def _layminei_set(self, value):
        self.pP.layminei= value
    layminei=property(_layminei_get, _layminei_set)

    def _sloperatiofactor_get(self):
        return self.pP.sloperatiofactor
    def _sloperatiofactor_set(self, value):
        self.pP.sloperatiofactor= value
    sloperatiofactor=property(_sloperatiofactor_get, _sloperatiofactor_set)

    def _sigsqei_get(self):
        return self.pP.sigsqei
    def _sigsqei_set(self, value):
        self.pP.sigsqei= value
    sigsqei=property(_sigsqei_get, _sigsqei_set)

    def _drho_get(self):
        return self.pP.drho
    def _drho_set(self, value):
        self.pP.drho= value
    drho=property(_drho_get, _drho_set)

    def _rhosconst1_get(self):
        return self.pP.rhosconst1
    def _rhosconst1_set(self, value):
        self.pP.rhosconst1= value
    rhosconst1=property(_rhosconst1_get, _rhosconst1_set)

    def _rhosconst2_get(self):
        return self.pP.rhosconst2
    def _rhosconst2_set(self, value):
        self.pP.rhosconst2= value
    rhosconst2=property(_rhosconst2_get, _rhosconst2_set)

    def _cstd1_get(self):
        return self.pP.cstd1
    def _cstd1_set(self, value):
        self.pP.cstd1= value
    cstd1=property(_cstd1_get, _cstd1_set)

    def _cstd2_get(self):
        return self.pP.cstd2
    def _cstd2_set(self, value):
        self.pP.cstd2= value
    cstd2=property(_cstd2_get, _cstd2_set)

    def _cstd3_get(self):
        return self.pP.cstd3
    def _cstd3_set(self, value):
        self.pP.cstd3= value
    cstd3=property(_cstd3_get, _cstd3_set)

    def _defaultcorr_get(self):
        return self.pP.defaultcorr
    def _defaultcorr_set(self, value):
        self.pP.defaultcorr= value
    defaultcorr=property(_defaultcorr_get, _defaultcorr_set)

    def _rhominfactor_get(self):
        return self.pP.rhominfactor
    def _rhominfactor_set(self, value):
        self.pP.rhominfactor= value
    rhominfactor=property(_rhominfactor_get, _rhominfactor_set)

    def _dzlaypeak_get(self):
        return self.pP.dzlaypeak
    def _dzlaypeak_set(self, value):
        self.pP.dzlaypeak= value
    dzlaypeak=property(_dzlaypeak_get, _dzlaypeak_set)

    def _azdzfactor_get(self):
        return self.pP.azdzfactor
    def _azdzfactor_set(self, value):
        self.pP.azdzfactor= value
    azdzfactor=property(_azdzfactor_get, _azdzfactor_set)

    def _dzeifactor_get(self):
        return self.pP.dzeifactor
    def _dzeifactor_set(self, value):
        self.pP.dzeifactor= value
    dzeifactor=property(_dzeifactor_get, _dzeifactor_set)

    def _dzeiweight_get(self):
        return self.pP.dzeiweight
    def _dzeiweight_set(self, value):
        self.pP.dzeiweight= value
    dzeiweight=property(_dzeiweight_get, _dzeiweight_set)

    def _dzlayfactor_get(self):
        return self.pP.dzlayfactor
    def _dzlayfactor_set(self, value):
        self.pP.dzlayfactor= value
    dzlayfactor=property(_dzlayfactor_get, _dzlayfactor_set)

    def _layconst_get(self):
        return self.pP.layconst
    def _layconst_set(self, value):
        self.pP.layconst= value
    layconst=property(_layconst_get, _layconst_set)

    def _layfalloffconst_get(self):
        return self.pP.layfalloffconst
    def _layfalloffconst_set(self, value):
        self.pP.layfalloffconst= value
    layfalloffconst=property(_layfalloffconst_get, _layfalloffconst_set)

    def _sigsqshortmin_get(self):
        return self.pP.sigsqshortmin
    def _sigsqshortmin_set(self, value):
        self.pP.sigsqshortmin= value
    sigsqshortmin=property(_sigsqshortmin_get, _sigsqshortmin_set)

    def _sigsqlayfactor_get(self):
        return self.pP.sigsqlayfactor
    def _sigsqlayfactor_set(self, value):
        self.pP.sigsqlayfactor= value
    sigsqlayfactor=property(_sigsqlayfactor_get, _sigsqlayfactor_set)

    def _defoazdzfactor_get(self):
        return self.pP.defoazdzfactor
    def _defoazdzfactor_set(self, value):
        self.pP.defoazdzfactor= value
    defoazdzfactor=property(_defoazdzfactor_get, _defoazdzfactor_set)

    def _defothreshfactor_get(self):
        return self.pP.defothreshfactor
    def _defothreshfactor_set(self, value):
        self.pP.defothreshfactor= value
    defothreshfactor=property(_defothreshfactor_get, _defothreshfactor_set)

    def _defomax_get(self):
        return self.pP.defomax
    def _defomax_set(self, value):
        self.pP.defomax= value
    defomax=property(_defomax_get, _defomax_set)

    def _sigsqcorr_get(self):
        return self.pP.sigsqcorr
    def _sigsqcorr_set(self, value):
        self.pP.sigsqcorr= value
    sigsqcorr=property(_sigsqcorr_get, _sigsqcorr_set)

    def _defolayconst_get(self):
        return self.pP.defolayconst
    def _defolayconst_set(self, value):
        self.pP.defolayconst= value
    defolayconst=property(_defolayconst_get, _defolayconst_set)

    def _eval_get(self):
        return self.pP.eval
    def _eval_set(self, value):
        self.pP.eval= value
    eval=property(_eval_get, _eval_set)

    def _unwrapped_get(self):
        return self.pP.unwrapped
    def _unwrapped_set(self, value):
        self.pP.unwrapped= value
    unwrapped=property(_unwrapped_get, _unwrapped_set)

    def _regrowconncomps_get(self):
        return self.pP.regrowconncomps
    def _regrowconncomps_set(self, value):
        self.pP.regrowconncomps= value
    regrowconncomps=property(_regrowconncomps_get, _regrowconncomps_set)

    def _initonly_get(self):
        return self.pP.initonly
    def _initonly_set(self, value):
        self.pP.initonly= value
    initonly=property(_initonly_get, _initonly_set)

    def _initmethod_get(self):
        return self.pP.initmethod
    def _initmethod_set(self, value):
        self.pP.initmethod= value
    initmethod=property(_initmethod_get, _initmethod_set)

    def _costmode_get(self):
        return self.pP.costmode
    def _costmode_set(self, value):
        self.pP.costmode= value
    costmode=property(_costmode_get, _costmode_set)

    def _dumpall_get(self):
        return self.pP.dumpall
    def _dumpall_set(self, value):
        self.pP.dumpall= value
    dumpall=property(_dumpall_get, _dumpall_set)

    def _verbose_get(self):
        return self.pP.verbose
    def _verbose_set(self, value):
        self.pP.verbose= value
    verbose=property(_verbose_get, _verbose_set)

    def _amplitude_get(self):
        return self.pP.amplitude
    def _amplitude_set(self, value):
        self.pP.amplitude= value
    amplitude=property(_amplitude_get, _amplitude_set)

    def _havemagnitude_get(self):
        return self.pP.havemagnitude
    def _havemagnitude_set(self, value):
        self.pP.havemagnitude= value
    havemagnitude=property(_havemagnitude_get, _havemagnitude_set)

    def _flipphasesign_get(self):
        return self.pP.flipphasesign
    def _flipphasesign_set(self, value):
        self.pP.flipphasesign= value
    flipphasesign=property(_flipphasesign_get, _flipphasesign_set)

    def _initmaxflow_get(self):
        return self.pP.initmaxflow
    def _initmaxflow_set(self, value):
        self.pP.initmaxflow= value
    initmaxflow=property(_initmaxflow_get, _initmaxflow_set)

    def _arcmaxflowconst_get(self):
        return self.pP.arcmaxflowconst
    def _arcmaxflowconst_set(self, value):
        self.pP.arcmaxflowconst= value
    arcmaxflowconst=property(_arcmaxflowconst_get, _arcmaxflowconst_set)

    def _maxflow_get(self):
        return self.pP.maxflow
    def _maxflow_set(self, value):
        self.pP.maxflow= value
    maxflow=property(_maxflow_get, _maxflow_set)

    def _krowei_get(self):
        return self.pP.krowei
    def _krowei_set(self, value):
        self.pP.krowei= value
    krowei=property(_krowei_get, _krowei_set)

    def _kcolei_get(self):
        return self.pP.kcolei
    def _kcolei_set(self, value):
        self.pP.kcolei= value

    kcolei=property(_kcolei_get, _kcolei_set)

    def _kpardpsi_get(self):
        return self.pP.kpardpsi
    def _kpardpsi_set(self, value):
        self.pP.kpardpsi= value
    kpardpsi=property(_kpardpsi_get, _kpardpsi_set)

    def _kperpdpsi_get(self):
        return self.pP.kperpdpsi
    def _kperpdpsi_set(self, value):
        self.pP.kperpdpsi= value
    kperpdpsi=property(_kperpdpsi_get, _kperpdpsi_set)

    def _threshold_get(self):
        return self.pP.threshold
    def _threshold_set(self, value):
        self.pP.threshold= value
    threshold=property(_threshold_get, _threshold_set)

    def _initdzr_get(self):
        return self.pP.initdzr
    def _initdzr_set(self, value):
        self.pP.initdzr= value
    initdzr=property(_initdzr_get, _initdzr_set)

    def _initdzstep_get(self):
        return self.pP.initdzstep
    def _initdzstep_set(self, value):
        self.pP.initdzstep= value
    initdzstep=property(_initdzstep_get, _initdzstep_set)

    def _maxcost_get(self):
        return self.pP.maxcost
    def _maxcost_set(self, value):
        self.pP.maxcost= value
    maxcost=property(_maxcost_get, _maxcost_set)

    def _costscale_get(self):
        return self.pP.costscale
    def _costscale_set(self, value):
        self.pP.costscale= value
    costscale=property(_costscale_get, _costscale_set)

    def _costscaleambight_get(self):
        return self.pP.costscaleambight
    def _costscaleambight_set(self, value):
        self.pP.costscaleambight= value
    costscaleambight=property(_costscaleambight_get, _costscaleambight_set)

    def _dnomincangle_get(self):
        return self.pP.dnomincangle
    def _dnomincangle_set(self, value):
        self.pP.dnomincangle= value
    dnomincangle=property(_dnomincangle_get, _dnomincangle_set)

    def _srcrow_get(self):
        return self.pP.srcrow
    def _srcrow_set(self, value):
        self.pP.srcrow= value
    srcrow=property(_srcrow_get, _srcrow_set)

    def _srccol_get(self):
        return self.pP.srccol
    def _srccol_set(self, value):
        self.pP.srccol= value
    srccol=property(_srccol_get, _srccol_set)

    def _p_get(self):
        return self.pP.p
    def _p_set(self, value):
        self.pP.p= value
    p=property(_p_get, _p_set)

    def _nshortcycle_get(self):
        return self.pP.nshortcycle
    def _nshortcycle_set(self, value):
        self.pP.nshortcycle= value
    nshortcycle=property(_nshortcycle_get, _nshortcycle_set)

    def _maxnewnodeconst_get(self):
        return self.pP.maxnewnodeconst
    def _maxnewnodeconst_set(self, value):
        self.pP.maxnewnodeconst= value
    maxnewnodeconst=property(_maxnewnodeconst_get, _maxnewnodeconst_set)

    def _maxnflowcycles_get(self):
        return self.pP.maxnflowcycles
    def _maxnflowcycles_set(self, value):
        self.pP.maxnflowcycles= value
    maxnflowcycles=property(_maxnflowcycles_get, _maxnflowcycles_set)

    def _maxcyclefraction_get(self):
        return self.pP.maxcyclefraction
    def _maxcyclefraction_set(self, value):
        self.pP.maxcyclefraction= value
    maxcyclefraction=property(_maxcyclefraction_get, _maxcyclefraction_set)

    def _sourcemode_get(self):
        return self.pP.sourcemode   
    def _sourcemode_set(self, value):
        self.pP.sourcemode = value
    sourcemode=property(_sourcemode_get, _sourcemode_set)

    def _cs2scalefactor_get(self):
        return self.pP.cs2scalefactor
    def _cs2scalefactor_set(self, value):
        self.pP.cs2scalefactor= value
    cs2scalefactor=property(_cs2scalefactor_get, _cs2scalefactor_set)

    def _ntilerow_get(self):
        return self.pP.ntilerow
    def _ntilerow_set(self, value):
        self.pP.ntilerow= value
    ntilerow=property(_ntilerow_get, _ntilerow_set)

    def _ntilecol_get(self):
        return self.pP.ntilecol
    def _ntilecol_set(self, value):
        self.pP.ntilecol= value
    ntilecol=property(_ntilecol_get, _ntilecol_set)

    def _rowovrlp_get(self):
        return self.pP.rowovrlp
    def _rowovrlp_set(self, value):
        self.pP.rowovrlp= value
    rowovrlp=property(_rowovrlp_get, _rowovrlp_set)

    def _colovrlp_get(self):
        return self.pP.colovrlp
    def _colovrlp_set(self, value):
        self.pP.colovrlp= value
    colovrlp=property(_colovrlp_get, _colovrlp_set)

    def _piecefirstrow_get(self):
        return self.pP.piecefirstrow
    def _piecefirstrow_set(self, value):
        self.pP.piecefirstrow= value
    piecefirstrow=property(_piecefirstrow_get, _piecefirstrow_set)

    def _piecefirstcol_get(self):
        return self.pP.piecefirstcol   
    def _piecefirstcol_set(self, value):
        self.pP.piecefirstcol= value
    piecefirstcol=property(_piecefirstcol_get, _piecefirstcol_set)

    def _piecenrow_get(self):
        return self.pP.piecenrow
    def _piecenrow_set(self, value):
        self.pP.piecenrow= value
    piecenrow=property(_piecenrow_get, _piecenrow_set)

    def _piecencol_get(self):
        return self.pP.piecencol
    def _piecencol_set(self, value):
        self.pP.piecencol= value
    piecencol=property(_piecencol_get, _piecencol_set)

    def _tilecostthresh_get(self):
        return self.pP.tilecostthresh
    def _tilecostthresh_set(self, value):
        self.pP.tilecostthresh= value
    tilecostthresh=property(_tilecostthresh_get, _tilecostthresh_set)

    def _minregionsize_get(self):
        return self.pP.minregionsize   
    def _minregionsize_set(self, value):
        self.pP.minregionsize   = value
    minregionsize=property(_minregionsize_get, _minregionsize_set)

    def _nthreads_get(self):
        return self.pP.nthreads
    def _nthreads_set(self, value):
        self.pP.nthreads= value
    nthreads=property(_nthreads_get, _nthreads_set)

    def _scndryarcflowmax_get(self):
        return self.pP.scndryarcflowmax
    def _scndryarcflowmax_set(self, value):
        self.pP.scndryarcflowmax= value
    scndryarcflowmax=property(_scndryarcflowmax_get, _scndryarcflowmax_set)

    def _tileedgeweight_get(self):
        return self.pP.tileedgeweight   
    def _tileedgeweight_set(self, value):
        self.pP.tileedgeweight   = value
    tileedgeweight=property(_tileedgeweight_get, _tileedgeweight_set)

    def _assembleonly_get(self):
        return self.pP.assembleonly   
    def _assembleonly_set(self, value):
        self.pP.assembleonly   = value
    assembleonly=property(_assembleonly_get, _assembleonly_set)

    def _rmtmptile_get(self):
        return self.pP.rmtmptile   
    def _rmtmptile_set(self, value):
        self.pP.rmtmptile   = value
    rmtmptile=property(_rmtmptile_get, _rmtmptile_set)

    def _tiledir_get(self):
        return self.pP.tiledir
    def _tiledir_set(self, value):
        strcpy(self.pP.tiledir, value)
    tiledir=property(_tiledir_get, _tiledir_set)

    def _minconncompfrac_get(self):
        return self.pP.minconncompfrac
    def _minconncompfrac_set(self, value):
        self.pP.minconncompfrac= value
    minconncompfrac=property(_minconncompfrac_get, _minconncompfrac_set)

    def _conncompthresh_get(self):
        return self.pP.conncompthresh
    def _conncompthresh_set(self, value):
        self.pP.conncompthresh= value
    conncompthresh=property(_conncompthresh_get, _conncompthresh_set)

    def _maxncomps_get(self):
        return self.pP.maxncomps
    def _maxncomps_set(self, value):
        self.pP.maxncomps= value
    maxncomps=property(_maxncomps_get, _maxncomps_set)

    def __init__(self):
        #self._formats=dict(complex_data=1, alt_line_data=3, alt_sample_data=4, float_data=2)
        #self._method=dict(nostatcosts=0, topo=1, defo=2, smooth=3)
        #self._algorithm=dict(mst=1, mcf=2)
        #self._transmit=dict(singleanttransmit=1, pingpong=2)
        pass

    cpdef unwrap_tile(self):
        print("Starting to unwrap...")
        print("Thanks for using pysnaphu!")

        iP=self.iP
        oP=self.oP
        pP=self.pP
        tP=self.tP

        #Set streams
        SetStreamPointers()

        #Check Parameters
        CheckParams(&iP, &oP, self.nwidth, self.nlines, &pP)

        #Start Unwrap
        UnwrapTile(&iP, &oP, &pP, &tP, self.nlines, self.nwidth)      

