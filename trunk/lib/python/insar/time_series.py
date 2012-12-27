import basic
import adore
import numpy as N
import pylab as P
import insar
import scipy
import scipy.integrate
from dateutil import parser
###############################################################
###############################################################
###############################################################
def select_pairs(scene, btemp, bperp, bdopp=None, btemp_limits=[0,400],bperp_limits=[0,300],bdopp_limits=[0,500]):
    """select_pairs(scene, btemp, bperp, bdopp, btemp_limits=[0,400],bperp_limits=[0,300],bdopp_limits=[0,500])
    master scene should have btemp=bperp=bdopp=0.
    """
    pairs=[]
    for m in N.r_[0:len(scene)]:
        for s in N.r_[0:len(scene)]:
            #if already included or master=slave skip
            if (m == s) | ((scene[s], scene[m]) in pairs ):
		continue
	    # if btemp is out of range skip
            if ( abs(btemp[m]-btemp[s])> btemp_limits[1] ) | ( abs(btemp[m]-btemp[s]) < btemp_limits[0] ):
                continue
	    # if bperp is out of range skip
            if ( abs(bperp[m]-bperp[s])> bperp_limits[1] ) | ( abs(bperp[m]-bperp[s]) < bperp_limits[0] ):
                continue
            if bdopp is not None:
		# if bdopp is out of range skip
                if ( abs(bdopp[m]-bdopp[s])> bdopp_limits[1] ) | ( abs(bdopp[m]-bdopp[s]) < btemp_limits[0] ):
                    continue
            pairs.append((scene[m], scene[s]));
    return pairs
###############################################################
###############################################################
###############################################################
def select_pairs_from_baselines(baselines_file,btemp_limits=[0,400],bperp_limits=[0,300],bdopp_limits=None):
    """select_pairs_from_baselines(baselines_file)
    """
    baseline_dtype=N.dtype([
          ('bt', float),
          ('bp', float),
          ('name', str, 80),
          ])
    A=N.loadtxt(baselines_file, dtype=baseline_dtype);
    scene=[x[2] for x in A];
    bperp=[x[1] for x in A];
    btemp=[x[0] for x in A];
    return select_pairs(scene, btemp, bperp, None, btemp_limits, bperp_limits, bdopp_limits)
###############################################################
###############################################################
###############################################################        
def bperp_btemp(drsFiles):
    from dateutil import parser
    
    mresfiles=[]
    sresfiles=[]
    iresfiles=[]
    for f in drsFiles:
        d=adore.drs2dict(f);
        mresfiles.append(d['general']['m_resfile'].strip());
        sresfiles.append(d['general']['s_resfile'].strip());
        iresfiles.append(d['general']['i_resfile'].strip());
    
    bperp=[]
    btemp=[]
    for f in N.r_[0:len(mresfiles)]:
        mobj=adore.dict2obj(adore.res2dict(mresfiles[f]))
        sobj=adore.dict2obj(adore.res2dict(sresfiles[f]))
        ires=adore.res2dict(iresfiles[f])
        iobj=adore.dict2obj(ires)
        bperp.append( iobj.coarse_orbits.Bperp )
        btemp.append( iobj.coarse_orbits.Btemp )
    return bperp, btemp        
###############################################################
###############################################################
###############################################################
#def plot_bperp_btemp(drsFiles):
#    fg=P.figure()
#    bperp,btemp=bperp_btemp(drsFiles)
#    scatter(btemp, bperp)
#    
#    return fg
###############################################################
###############################################################
###############################################################        

def average_coherence_adore(iresfiles=None, drsFiles=None):
    """ avg_coherence=average_coherence_adore(iresfiles=None, drsFiles=None):
    """
    from dateutil import parser
    
    if drsFiles is not None:
        iresfiles=[]
        for f in drsFiles:
            d=adore.drs2dict(f);
            iresfiles.append(d['general']['i_resfile'].strip());
    
    coh=[]
    for f in N.r_[0:len(iresfiles)]:
        ires=adore.res2dict(iresfiles[f])
        iobj=adore.dict2obj(ires)
        coh.append(  adore.getProduct(ires,'coherence') );
    coh=N.rollaxis(N.dstack(coh),2,0)
    return coh.mean(0);
###############################################################
###############################################################
###############################################################        
def select_single_master(bperp,scene):
    return scene[N.argmin(abs(bperp-N.mean(bperp)))]
###############################################################
###############################################################
###############################################################        
def select_single_master_from_baselines(baselines_file):
    baseline_dtype=N.dtype([
          ('bt', float),
          ('bp', float),
          ('name', str, 80),
          ])
    A=N.loadtxt(baselines_file, dtype=baseline_dtype);
    scene=[x[2] for x in A];
    bperp=[x[1] for x in A];
    return select_single_master(bperp,scene)
    
