#!/usr/bin/env python

import sys
import pylab
import adore

def main(argv=None):
  if argv is None:
    argv=sys.argv
  iresfile=argv[1];
  ires=adore.res2dict(iresfile);
  A=ires['coarse_correl']['results'];
  az=ires['coarse_correl']['Coarse_correlation_translation_lines'];
  rg=ires['coarse_correl']['Coarse_correlation_translation_pixels'];
#figure1
  pylab.figure()
  pylab.title('Coarse Correlation Results')
  Q=pylab.quiver(A[:,2], A[:,1], A[:,5], A[:,4], A[:,3]);
  azAvg=round(pylab.np.mean(A[:,3]));
  rgAvg=round(pylab.np.mean(A[:,4]));
  qk = pylab.quiverkey(Q, 0.33, 0.92, azAvg, ('%d [px az]' % (azAvg)), labelpos='W', fontproperties={'weight': 'bold'})
  qk = pylab.quiverkey(Q, 0.66, 0.92, rgAvg, ('%d [px rg]' % (rgAvg)), labelpos='W', fontproperties={'weight': 'bold'})
  pylab.colorbar()

#figure2
  pylab.figure()
  pylab.title('Coarse Correlation Deviations')
  Q=pylab.quiver(A[:,2], A[:,1], A[:,5]-rg, A[:,4]-az, A[:,3]);
  azStd=round(pylab.np.std(A[:,3]-az));
  rgStd=round(pylab.np.std(A[:,4]-rg));
  qk = pylab.quiverkey(Q, 0.33, 0.92, azStd, ('%d [px az]' % (azStd)), labelpos='W', fontproperties={'weight': 'bold'})
  qk = pylab.quiverkey(Q, 0.66, 0.92, rgStd, ('%d [px rg]' % (rgStd)), labelpos='W', fontproperties={'weight': 'bold'})

  pylab.colorbar()
  pylab.show()

if __name__ == "__main__":
    sys.exit(main())
