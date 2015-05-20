#!/usr/bin/env python

import sys
import pylab
import adore
import pdb

def main(argv=None):
  if argv is None:
    argv=sys.argv
  drsfile=argv[1];
  try:
    ct=float(argv[2]);
  except:
    ct=0.0
  if drsfile is not None:
    d=adore.drs2dict(drsfile);
    mresfile=d['general']['m_resfile'].strip();
    sresfile=d['general']['s_resfile'].strip();
    iresfile=d['general']['i_resfile'].strip();

  iobj=adore.dict2obj(adore.res2dict(iresfile));
  mobj=adore.dict2obj(adore.res2dict(mresfile));
  sobj=adore.dict2obj(adore.res2dict(sresfile));
  A=iobj.fine_coreg.results; #ires['fine_coreg']['results'];
  A=A[A[:,5]>ct,:]

#figure
  pylab.figure()
  pylab.title('Range: Fine Correlation - Coregistration Polynomial')
  rg=adore.basic.rescale(A[:,2], [-2,2], arrlim=[mobj.crop.First_pixel, mobj.crop.Last_pixel]);
  az=adore.basic.rescale(A[:,1], [-2,2], arrlim=[mobj.crop.First_line, mobj.crop.Last_line]);
  pixelOffset=adore.polyval(rg, az, iobj.comp_coregpm.Estimated_coefficientsP);
  lineOffset =adore.polyval(rg, az, iobj.comp_coregpm.Estimated_coefficientsL);
  Q=pylab.quiver(A[:,2], A[:,1], A[:,4]-pixelOffset, A[:,3]-lineOffset, A[:,5]);
  azStd=round(pylab.np.std(A[:,3]-lineOffset));
  rgStd=round(pylab.np.std(A[:,4]-pixelOffset));
  qk = pylab.quiverkey(Q, 0.33, 0.92, azStd, ('%d [px az]' % (azStd)), labelpos='W', fontproperties={'weight': 'bold'})
  qk = pylab.quiverkey(Q, 0.66, 0.92, rgStd, ('%d [px rg]' % (rgStd)), labelpos='W', fontproperties={'weight': 'bold'})
  pylab.colorbar()
  pylab.show()

if __name__ == "__main__":
    sys.exit(main())

