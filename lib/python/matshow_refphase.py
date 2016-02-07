#!/usr/bin/env python

import sys
import pylab
import adore
import pdb

def main(argv=None):
  if argv is None:
    argv=sys.argv
  iresfile=argv[1];
  try:
    ct=float(argv[2]);
  except:
    ct=0.0
  ires=adore.res2dict(iresfile);
  A=ires['fine_coreg']['results'];
  A=A[A[:,5]>ct,:]
  az=int(ires['fine_coreg']['Initial offsets'].split(',')[0]);
  rg=int(ires['fine_coreg']['Initial offsets'].split(',')[1]);
#figure1
  pylab.figure()
  pylab.title('Fine Correlation Results')
  Q=pylab.quiver(A[:,2], A[:,1], A[:,4], A[:,3], A[:,5]);
  azAvg=round(pylab.np.mean(A[:,3]));
  rgAvg=round(pylab.np.mean(A[:,4]));
  qk = pylab.quiverkey(Q, 0.33, 0.92, azAvg, ('%d [px az]' % (azAvg)), labelpos='W', fontproperties={'weight': 'bold'})
  qk = pylab.quiverkey(Q, 0.66, 0.92, rgAvg, ('%d [px rg]' % (rgAvg)), labelpos='W', fontproperties={'weight': 'bold'})
  pylab.colorbar()

#figure2
  pylab.figure()
  pylab.title('Fine Correlation Deviations')
  pylab.quiver(A[:,2], A[:,1], A[:,4]-rg, A[:,3]-az, A[:,5]);
  Q=pylab.quiver(A[:,2], A[:,1], A[:,4]-rg, A[:,3]-az, A[:,5]);
  azStd=round(pylab.np.std(A[:,3]-az));
  rgStd=round(pylab.np.std(A[:,4]-rg));
  qk = pylab.quiverkey(Q, 0.33, 0.92, azStd, ('%d [px az]' % (azStd)), labelpos='W', fontproperties={'weight': 'bold'})
  qk = pylab.quiverkey(Q, 0.66, 0.92, rgStd, ('%d [px rg]' % (rgStd)), labelpos='W', fontproperties={'weight': 'bold'})
  pylab.colorbar()
  pylab.show()

if __name__ == "__main__":
    sys.exit(main())
