import basic
import adore
import numpy as N
import pylab as P
import insar
import scipy
import scipy.integrate
import os
from dateutil import parser
###############################################################
###############################################################
###############################################################
def select_pairs(scene, btemp, bperp, bdopp=None, btemp_limits=[0,400],bperp_limits=[0,300],bdopp_limits=[0,500], method='all', exclude=''):
    """select_pairs(scene, btemp, bperp, bdopp, btemp_limits=[0,400],bperp_limits=[0,300],bdopp_limits=[0,500])
    master scene should have btemp=bperp=bdopp=0.
    """
    pairs=[]
    if method=='all':
        for m in N.r_[0:len(scene)]:
            for s in N.r_[0:len(scene)]:
                #skip (continue) if pair is excluded   
                if ( scene[m] in exclude ) or ( scene[s] in exclude):
                    continue
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
                    if ( abs(bdopp[m]-bdopp[s])> bdopp_limits[1] ) | ( abs(bdopp[m]-bdopp[s]) < bdopp_limits[0] ):
                        continue
                pairs.append((scene[m], scene[s]));
    elif method=='delaunay':
        # get delaunay triangulation
        cens, edges, tri, neig = P.matplotlib.delaunay.delaunay(btemp, bperp)        
        # remove long pairs
        for e in edges:
            m=e[0]
            s=e[1]
            #skip (continue) if pair is excluded
            if (( scene[m] in exclude ) or ( scene[s] in exclude)):
                continue
            #Skip (continue) if pair is out of range
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
                if ( abs(bdopp[m]-bdopp[s])> bdopp_limits[1] ) | ( abs(bdopp[m]-bdopp[s]) < bdopp_limits[0] ):
                    continue
            #otherwise add
            pairs.append((scene[m], scene[s])) 
    return pairs
###############################################################
###############################################################
###############################################################
def select_pairs_from_baselines(baselines_file,btemp_limits=[0,400],bperp_limits=[0,300],bdopp_limits=[0,500], method="all", exclude=''):
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
    return select_pairs(scene, btemp, bperp, None, btemp_limits, bperp_limits, bdopp_limits, method, exclude=exclude)
        
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
def bperp_btemp_master_slave(drsFiles=None):
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
    master=[]
    slave=[]
    for f in N.r_[0:len(mresfiles)]:
        mobj=adore.dict2obj(adore.res2dict(mresfiles[f]))
        sobj=adore.dict2obj(adore.res2dict(sresfiles[f]))
        ires=adore.res2dict(iresfiles[f])
        iobj=adore.dict2obj(ires)
        master.append( parser.parse(mobj.readfiles.First_pixel_azimuth_time) )
        slave.append( parser.parse(sobj.readfiles.First_pixel_azimuth_time) )
        bperp.append( iobj.coarse_orbits.Bperp )
        btemp.append( iobj.coarse_orbits.Btemp )
    return bperp, btemp, master, slave        
###############################################################
###############################################################
###############################################################
def plot_bperp_btemp(drsFiles):
    fg=P.figure()
    bperp,btemp,master,slave=bperp_btemp_master_slave(drsFiles)
    
    K=len(bperp)
    allDates=master + slave #merge master and slave lists
    allDates=N.sort(list(set(allDates)));
    I=len(allDates); #Number of images (dates)
    temporalSampling=[x.days for x in N.diff(N.sort(list(set(allDates)))).ravel() ]
    A=N.zeros([K+1,I]);
    tS=temporalSampling
    for k in xrange(K):
        A[k,:]=(allDates==master[k])*-1+(allDates==slave[k])*1; 
    A[-1,0]=1
    t=N.dot(N.linalg.pinv(A),btemp+[0]) #merge zero to the end of list
    p=N.dot(N.linalg.pinv(A),bperp+[0]) #merge zero to the end of list
    
    P.scatter(t,p)
    dateList=allDates.copy()
    for k in xrange(K):
        tk=t[allDates==master[k]]
        pk=p[allDates==master[k]]
        ts=t[allDates==slave[k]]
        ps=p[allDates==slave[k]]
        #P.plot([tk, tk+btemp[k]], [pk, pk+bperp[k]] )
        P.plot([tk, ts], [pk, ps] )
        if any(allDates) == False:
            continue
        if master[k] in dateList:
          P.annotate(str(master[k].date()), xy=(tk, pk), xytext=(tk, pk+10))
          dateList[N.where(allDates==master[k])]=None          
        if slave[k] in dateList:
          P.annotate(str(slave[k].date()), xy=(ts, ps), xytext=(ts, ps+10))
          dateList[N.where(allDates==slave[k])]=None          
      
    return fg
###############################################################
###############################################################
###############################################################        
def plot_bperp_btemp(baselines_file, pairs_file):
    '''plot_bperp_btemp(baselines_file, pairs_file)
    '''
    fg=P.figure()
    baseline_dtype=N.dtype([
          ('bt', float),
          ('bp', float),
          ('name', str, 80),
          ])
    A=N.loadtxt(baselines_file, dtype=baseline_dtype);
    scene=[x[2] for x in A];
    bperp=[x[1] for x in A];
    btemp=[x[0] for x in A];
    pairs_dtype=N.dtype([
          ('master', str,80),
          ('slave', str,80),
          ])
    B=N.loadtxt(pairs_file, dtype=pairs_dtype, delimiter=',');
    master=[x[1] for x in B];
    slave =[x[0] for x in B];
    
    P.scatter(btemp,bperp)
    K=len(btemp)
    I=len(master)
    print("Plotting %d scenes and %d interferograms." % (K, I) )
    dateList=scene[:] #copy the list
    for k in xrange(I):
        mi=[ i for i,x in enumerate(scene) if x == master[k] ][0]
        si=[ i for i,x in enumerate(scene) if x == slave[k] ][0]
        
        tm=btemp[mi]
        pm=bperp[mi]
        ts=btemp[si]
        ps=bperp[si]
        #P.plot([tk, tk+btemp[k]], [pk, pk+bperp[k]] )
        P.plot([tm, ts], [pm, ps] )
        if any(dateList) == False:
            continue
        if dateList[mi] is not None:
          P.annotate(master[k], xy=(tm, pm), xytext=(tm, pm+10))
          dateList[mi]=None          
        if dateList[si] is not None:
          P.annotate(slave[k], xy=(ts, ps), xytext=(ts, ps+10))
          dateList[si]=None          
    unusedI12s=[ i for i,x in enumerate(dateList) if x is not None ]
    for k in unusedI12s:
      tm=btemp[k]
      pm=bperp[k]
      P.annotate(scene[k], xy=(tm, pm), xytext=(tm, pm+10))
    return fg
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
###############################################################
###############################################################
###############################################################        
def estimate_overlap(baselinesFolder,buffers=[200,200], masterRes=None):
    """estimate_overlap(baselinesFolder, buffers[az_buf, rg_buf])
       az_buf=200
       rg_buf=200
       ex:
       baselinesFolder=setobj.adore.baselinesfolder.strip('"')
       estimate_overlap(baselinesFolder, [400,400])
    """
    import glob
    if masterRes is not None:
        mobj=adore.dict2obj(adore.res2dict( masterRes ))
    
    ifiles=glob.glob(baselinesFolder+'/*_*.res')
    i12s=[]    #interferogram objects list
    master=[]  #master names list
    slave=[]   #slave names list
    lines=[]   #list of translation lines (az)
    pixels=[]  #list of translation pixels (rg)
    for f in ifiles:
        d=adore.res2dict(f) #dictionary
        #i12s.append(adore.dict2obj(d))
        iobj=adore.dict2obj(d)
        master.append(os.path.splitext(os.path.basename(f))[0].split('_')[0])
        slave.append(os.path.splitext(os.path.basename(f))[0].split('_')[1])
        lines.append(iobj.coarse_orbits.Coarse_orbits_translation_lines)
        pixels.append(iobj.coarse_orbits.Coarse_orbits_translation_pixels)
        
    K=len(ifiles)            #number of interferograms
    allDates=master + slave  #merge master and slave lists
    allDates=N.sort(list(set(allDates)));
    I=len(allDates); #Number of images (dates)
    A=N.zeros([K+1,I]);
    
    if masterRes is None:
        masterScene=0
    else:
        masterScene=os.path.splitext(os.path.basename(masterRes))[0]
        masterScene=(allDates==masterScene)    

    for k in xrange(K):
        A[k,:]=(allDates==master[k])*-1+(allDates==slave[k])*1; 
    A[-1,masterScene]=1
    l=N.dot(N.linalg.pinv(A),lines+[0]) #merge zero to the end of list
    p=N.dot(N.linalg.pinv(A),pixels+[0]) #merge zero to the end of list

    neg_line_off=min(l[l<0])             #negative line offset
    pos_line_off=max(l[l>0])             #positive line offset
    neg_pix_off=min(p[p<0])             #negative px offset
    pos_pix_off=max(p[p>0])             #positive px offset

    if masterRes is not None:
        return -1
#        if lo > 0:
#            lmin=0
#            if mobj.process_control.oversample == 1:
#                lmax=mobj.oversample.Last_line-lo/mobj.oversample.Multilookfactor_azimuth_direction            
#            else:
#                lmax=mobj.crop.Last_line-lo                        
#        else:
#            if mobj.process_control.oversample == 1:
#                lmin=mobj.oversample.First_line-l0/mobj.oversample.Multilookfactor_azimuth_direction
#                lmax=mobj.oversample.Last_line
#            else:
#                lmin=mobj.crop.First_line-l0
#                lmax=mobj.crop.Last_line
#        if po > 0:
#            pmin=0
#            if mobj.process_control.oversample == 1:
#                pmax=mobj.oversample.Last_pixel-po/mobj.oversample.Multilookfactor_range_direction            
#            else:
#                pmax=mobj.crop.Last_line-po                        
#        else:
#            if mobj.process_control.oversample == 1:
#                pmin=mobj.oversample.First_pixel-p0/mobj.oversample.Multilookfactor_range_direction
#                pmax=mobj.oversample.Last_pixel
#            else:
#                lmin=mobj.crop.First_pixel-p0
#                lmax=mobj.crop.Last_pixel
#        return [mobj.crop.First_line+lo, po]              
    else:
        return [neg_line_off, pos_line_off, neg_pix_off, pos_pix_off]    

