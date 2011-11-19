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
  pylab.quiver(A[:,2], A[:,1], A[:,5], A[:,4], A[:,3]);
  pylab.colorbar()
#figure2

  pylab.figure()
  pylab.title('Coarse Correlation Deviations')
  pylab.quiver(A[:,2], A[:,1], A[:,5]-rg, A[:,4]-az, A[:,3]);
  pylab.colorbar()
  pylab.show()

if __name__ == "__main__":
    sys.exit(main())