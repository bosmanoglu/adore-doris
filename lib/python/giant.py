#!/usr/bin/env python
import os, re
#import numpy as np
import basic 

try:
  import tsinsar as ts
except:
  ts=None
  pass

class Object:
    """ADORE-GIAnT Object
    
    """
                
    def __init__(self, folder, dataxml='data.xml', procxml='sbas.xml'):
        self.io=basic.DictObj()
        self.io.folder=folder
        if not os.path.exists(folder):
            #Initialize barebones
            pass
        else:
            try:
                self.io.dparsxml=os.path.join(self.io.folder, dataxml)
                self.dpars=ts.TSXML(self.io.dparsxml, True);
            except:
                self.io.dparsxml=None
                self.dpars=None
            try:
                self.io.pparsxml=os.path.join(self.io.folder, procxml)
                self.ppars=ts.TSXML(self.io.pparsxml, True);
            except:
                self.io.pparsxml=None
                self.ppars=None
            if os.path.exists(os.path.join(self.dpars.data.dirs.h5dir, 'RAW-STACK.h5')):
                self.RAW_STACK=ts.loadh5(os.path.join(self.dpars.data.dirs.h5dir, 'RAW-STACK.h5'))
            if os.path.exists(os.path.join(self.dpars.data.dirs.h5dir, 'PROC-STACK.h5')):
                self.PROC_STACK=ts.loadh5(os.path.join(self.dpars.data.dirs.h5dir, 'PROC-STACK.h5'))
            if os.path.exists(os.path.join(self.dpars.data.dirs.h5dir, 'LS-PARAMS.h5')):
                self.LS_PARAMS=ts.loadh5(os.path.join(self.dpars.data.dirs.h5dir, 'LS-PARAMS.h5'))

