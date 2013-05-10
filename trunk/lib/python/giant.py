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
            if os.path.exists(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'RAW-STACK.h5')):
                self.RAW_STACK=ts.loadh5(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'RAW-STACK.h5'))
            if os.path.exists(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'PROC-STACK.h5')):
                self.PROC_STACK=ts.loadh5(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'PROC-STACK.h5'))
            if os.path.exists(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'LS-PARAMS.h5')):
                self.LS_PARAMS=ts.loadh5(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'LS-PARAMS.h5'))
            if os.path.exists(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'NSBAS-PARAMS.h5')):
                self.NSBAS_PARAMS=ts.loadh5(os.path.join(self.io.folder, self.dpars.data.dirs.h5dir, 'NSBAS-PARAMS.h5'))

    def ensemble_coherence(self, sol, weight=None, ref=None):
        '''ensemble_coherence(sol,weight=None)
        Calculates the ensemble coherence based on complex interferograms (G.RAW-STACK) and solutions (G.LS-PARAMS). 
        weight: 'long' or 'short' for btemp
        '''
#        if ref is None:
#          ref=[self.dpars.data.subimage.rymin, self.dpars.data.subimage.rymax, self.dpars.data.subimage.rxmin, self.dpars.data.subimage.rxmax];
#        elif len(ref)==2:
#          print('Expanding reference point to 3x3 neighborhood.')
#          ref=[ref[0]-1,ref[0]+1, ref[1]-1,ref[1]+1];
#        elif len(ref)==4:
#          pass
#        else:
#          raise ValueError("Reference point should be an (x,y) tuple or [xmin,xmax,ymin,ymax].")
#          return
#        Jmat=self.RAW_STACK['Jmat']
#        recons=sol['rawts']
        dS=sol['rawts'].shape #dataShape
#        recons=basic.tile(-recons[:,ref[0]:ref[1], ref[2]:ref[3]].mean(axis=-1).mean(axis=-1), (dS[1]*dS[2],1)).T+recons.reshape([dS[0], dS[1]*dS[2]])
#        recons=recons.reshape([dS[0], dS[1]*dS[2]])
#        recons_interf=(basic.dot(Jmat, recons)/1000.)*(4.0*basic.pi/self.dpars.data.master.wavelength) #convert to meters and then radians.
#        #data=self.RAW_STACK['igram']
#        data=self.PROC_STACK['figram']        
#        dSi=data.shape[0]
#        data=basic.tile(data[:,ref[0]:ref[1], ref[2]:ref[3]].mean(axis=-1).mean(axis=-1), (dS[1]*dS[2],1)).T+data.reshape([dSi, dS[1]*dS[2]])
#        data_diff=basic.exp(1j*basic.wrapToPi(data.reshape(recons_interf.shape)-recons_interf));
        data_diff=basic.exp(1j*self.residual(sol, ref=ref, units='rad'));
        dSi=data_diff.shape[0]
        data_diff=data_diff.reshape(data_diff.shape[0], data_diff.shape[1]*data_diff.shape[2])
        keep=list(basic.arange(dSi));        
        if any(basic.isnan(data_diff.ravel())):
            #find and remove if there are interferograms that are all nan.
            for k in xrange(data_diff.shape[0]):
                if all(basic.isnan(data_diff[k,:])):
                    keep.remove(k);
        data_diff=data_diff[keep,:];
        if weight is None:
            #ensemble_coherence=abs(basic.exp(1.j*(data_diff)).mean(axis=0))            
            ensemble_coherence=abs(data_diff.sum(axis=0))/dSi           
        elif weight=='long':
            weight=abs(basic.dot(self.RAW_STACK['Jmat'], self.RAW_STACK['tims']))
            weight=weight.reshape([1,dSi])
            ensemble_coherence=abs(basic.dot(weight, basic.exp(1.j*(data_diff)))/weight.sum())
        elif weight=='short':
            weight=abs(basic.dot(self.RAW_STACK['Jmat'], self.RAW_STACK['tims']))
            wmin=weight.min();wmax=weight.max()
            weight=wmax-weight.reshape([1,dSi])+wmin #flip the weights
            ensemble_coherence=abs(basic.dot(weight, basic.exp(1.j*(data_diff)))/weight.sum())
        else:
            print "weight can be :'long', 'short' or None."
            return False
        return ensemble_coherence.reshape([dS[1], dS[2]])
        
    def residual(self, sol, show=False, ref=None, units='mm'):
        '''residual(sol,show=False)
        Calculates residual phase based on complex interferograms (G.RAW-STACK) and solutions (G.LS-PARAMS). 
        '''
        if ref is None:
          ref=[self.dpars.data.subimage.rymin, self.dpars.data.subimage.rymax, self.dpars.data.subimage.rxmin, self.dpars.data.subimage.rxmax];
        elif len(ref)==2:
          print('Expanding reference point to 3x3 neighborhood.')
          ref=[ref[0]-1,ref[0]+1, ref[1]-1,ref[1]+1];
        elif len(ref)==4:
          pass
        else:
          raise ValueError("Reference point should be an (x,y) tuple or [xmin,xmax,ymin,ymax].")
          return
        Jmat=self.RAW_STACK['Jmat']
        recons=sol['rawts']
        subimage=self.dpars.data.subimage
        dS=recons.shape #dataShape
        recons=basic.tile(-recons[:,ref[0]:ref[1], ref[2]:ref[3]].mean(axis=-1).mean(axis=-1), (dS[1]*dS[2],1)).T+recons.reshape([dS[0], dS[1]*dS[2]])
        #recons=basic.tile(-recons[:,subimage.rxmin:subimage.rxmax, subimage.rymin:subimage.rymax].mean(axis=-1).mean(axis=-1), (dS[1]*dS[2],1)).T+recons.reshape([dS[0], dS[1]*dS[2]])
        recons=recons.reshape([dS[0], dS[1]*dS[2]])
        recons_interf=basic.dot(Jmat, recons);
        #(basic.dot(Jmat, recons)/1000.)*(4.0*basic.pi/self.dpars.data.master.wavelength) #convert to meters and then radians.
        #data=self.RAW_STACK['igram']
        data=self.PROC_STACK['figram']        
        dSi=data.shape[0]
        data=basic.tile(data[:,ref[0]:ref[1], ref[2]:ref[3]].mean(axis=-1).mean(axis=-1), (dS[1]*dS[2],1)).T+data.reshape([dSi, dS[1]*dS[2]])
        data_diff=data.reshape(recons_interf.shape)-recons_interf;
        #data_diff=basic.wrapToPi(data.reshape(recons_interf.shape)-recons_interf);        
        #ensemble_coherence=abs(residual.sum(axis=0))/abs(residual).sum(axis=0)
        #icoh=insar.stdpha2coh(residual).reshape(cintA.shape)
        if units == 'mm':
          residual=data_diff.reshape(dSi, dS[1], dS[2])
        else:
          residual=data_diff.reshape(dSi, dS[1], dS[2])*(4.0*basic.pi/(self.dpars.data.master.wavelength*1000)) #divide by 4pi/wavelength in mm
        if show:
          basic.graphics.matshowN(residual);
        return residual        

#    def misfit(self, sol, show=False):
#        '''residual(sol,show=False)
#        Calculates misfit based on complex interferograms (G.RAW-STACK) and solutions (G.LS-PARAMS). 
#        '''
#        Jmat=self.RAW_STACK['Jmat']
#        recons=sol['recons']
#        subimage=self.dpars.data.subimage
#        dS=recons.shape #dataShape
#        #recons=basic.tile(-recons[:,subimage.rxmin:subimage.rxmax, subimage.rymin:subimage.rymax].mean(axis=-1).mean(axis=-1), (dS[1]*dS[2],1)).T+recons.reshape([dS[0], dS[1]*dS[2]])
#        recons=recons.reshape([dS[0], dS[1]*dS[2]])
#        recons_interf=(basic.dot(Jmat, recons)/1000.)*(4.0*basic.pi/self.dpars.data.master.wavelength) #convert to meters and then radians.
#        data=self.RAW_STACK['igram']
#        dSi=data.shape[0]
#        #data=basic.tile(-data[:,subimage.rxmin:subimage.rxmax, subimage.rymin:subimage.rymax].mean(axis=-1).mean(axis=-1), (dS[1]*dS[2],1)).T+data.reshape([dSi, dS[1]*dS[2]])
#        data_diff=basic.wrapToPi(data.reshape(recons_interf.shape)-recons_interf);        
#        #ensemble_coherence=abs(residual.sum(axis=0))/abs(residual).sum(axis=0)
#        #icoh=insar.stdpha2coh(residual).reshape(cintA.shape)
#        residual=data_diff.reshape(data.shape)
#        stdpha=
#        if show:
#          basic.graphics.matshowN(residual);
#        return misfit  
            
        
