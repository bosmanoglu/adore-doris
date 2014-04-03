#pixel_offsets.py

import numpy as N
def pixel_offsets(rgo, lam, las, avg_rgo=None, same_side=True):
    """pixel_offsets(az, rg, azo, rgo, lam, las, avg_azo=None, avg_rgo=None, sameSide=True):
    rgo: range offset (w.r.t. master)
    lam: look-angle for master (radians)
    las: look-angle for slave  (radians)
    avg-rgo: average range offset
    same_side: image is acquired same side. 
    """
    if avg_rgo is None:
        avg_rgo=mean(rgo)
    return [ (rgo[x]-avg_rgo) / (_cot(lam[x]) - _cot(las[x])) for x in range(0,len(rgo))]
    
def _cot(angle_radian):
    return 1./N.tan(angle_radian)


