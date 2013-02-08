#!/usr/bin/env python
'''Example script for creating XML files for use with the SBAS processing
chain.  This script is supposed to be copied to the working directory and
modified as needed.'''

''' 
CHANGELOG:
20121218 Modified for ADORE 
TODO: 
set r
'''

import tsinsar as ts
#import argparse
import numpy as np
import dateutil
import basic

#def parse():
#    parser= argparse.ArgumentParser(description='Preparation of XML files for setting up the processing chain. Check tsinsar/tsxml.py for details on the parameters.')
#    parser.parse_args()


#parse()

#reference point
coh=adore.getProduct(iobj.coherence)
ref=basic.ind2sub(coh.shape, coh.argmax())
del coh

if os.path.exists(setobj.comprefdem.crd_out_dem_lp.strip('"')):
  hgtfile=setobj.comprefdem.crd_out_dem_lp.strip('"')
  demerr=True
else:
  hgtfile=''
  demerr=False
g = ts.TSXML('data')
g.prepare_data_xml([iobj.resfile,
                   mobj.resfile],
                   proc='DORIS',looks=1, cohth=0., mask='', 
            	   xlim=None, ylim=None, 
            	   rxlim=[ref[0]-1,ref[0]+1], rylim=[ref[1]-1,ref[1]+1], 
            	   latfile='',
                   lonfile='', 
                   hgtfile=hgtfile, 
                   inc=iobj.coarse_orbits.inc_angle,
                   h5dir='Stack',
                   atmosdir='Atmos',figsdir='Figs',respdir='RESP',
                   unwfmt='FLT',demfmt='FLT',corfmt='FLT',
                   chgendian=False,masktype='f4',
                   endianlist=['UNW','COR','HGT'])
g.writexml('data.xml')

masterdate=dateutil.parser.parse(mobj.readfiles.First_pixel_azimuth_time).strftime('%Y%m%d')
g = ts.TSXML('params')
g.prepare_sbas_xml(nvalid=30,netramp=True,atmos='',demerr=True,uwcheck=False,regu=True,masterdate=masterdate,filt=1.0)
g.writexml('sbas.xml')
