#!/usr/bin/env python

import sys
import pylab
import numpy as np
#import adore

def main(argv=None):
  if argv is None:
    argv=sys.argv
  baselinesfile=argv[1];
  baselines=np.loadtxt(baselinesfile);
#figure1
  pylab.figure()
  pylab.title('Baseline Plot')  
  pylab.scatter(baselines[:,0], baselines[:,1]);
  pylab.xlabel('Time (Days)');
  pylab.ylabel('Perpendicular Baseline (m)');
  for k in xrange(baselines.shape[0]):
    pylab.annotate(str(baselines[k,2]),xy=(baselines[k,0]-20,baselines[k,1]+20))
  pylab.show()

if __name__ == "__main__":
    sys.exit(main())
