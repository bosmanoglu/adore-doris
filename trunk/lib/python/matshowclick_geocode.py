#!/usr/bin/env python

import sys
import adore
import pdb
#from mayavi import mlab
import pylab as pl
from scipy import interpolate
from mpl_toolkits.basemap import Basemap
import numpy 

def main(argv=None):
  A=adore.Object()
  if argv is None:
    argv=sys.argv
  iresfile=argv[1];
  try:    
    product=argv[2];
  except:
    product='geocoding'
  ires=adore.res2dict(iresfile);
  iobj=adore.dict2obj(ires);  
  lat=adore.getProduct(iobj.geocoding, filename=iobj.geocoding.Data_output_file_lamda)
  lon=adore.getProduct(iobj.geocoding, filename=iobj.geocoding.Data_output_file_phi)
  if product=='geocoding':
    hei=adore.getProduct(iobj.geocoding, filename=iobj.geocoding.Data_output_file_hei)
  else:
    #check if includes colon:
    if ":" in product:
      filename=product.split(':')[1]
      product=product.split(':')[0]  
    else:
      filename=None  
    #hei is actually any data at this point...   
    hei=adore.getProduct(ires, product, filename=filename)

  #d0 is longitude, d1 is latitude
  d0,d1=numpy.meshgrid(numpy.linspace(lat.min(),lat.max(), lon.shape[1]), 
    numpy.linspace(lon.min(), lon.max(), lon.shape[0]))  
  if lat[0,0] > 0: #northern hemisphere
    if d1[0,0]<d1[-1,0]:
      d1=numpy.flipud(d1)
  
  hei_gridded = interpolate.griddata((lon.ravel(),lat.ravel()), hei.ravel(), (d1, d0), method='linear')
  
  #set-up basemap
  print ('Please wait... Generating map\n')
  m = Basemap(llcrnrlon=d0.min(), llcrnrlat=d1.min(), urcrnrlon=d0.max(), urcrnrlat=d1.max(), 
    resolution='f', area_thresh=1., projection='cyl')
  m.imshow(hei_gridded, interpolation='nearest', origin='upper')
  m.drawcoastlines(color='w',linewidth=0.8)
  m.drawmapboundary() # draw a line around the map region
  m.drawrivers() 
  m.drawparallels(numpy.arange(int(d1.min()), int(d1.max()), 1),linewidth=0.2,labels=[1,0,0,0])  
  m.drawmeridians(numpy.arange(int(d0.min()), int(d0.max()), 1),linewidth=0.2,labels=[0,0,0,1])  
  
#MAYAVI TAKES TOO LONG  
#  #visualize points
#  pts =mlab.points3d(lon.ravel(), lat.ravel(), hei.ravel(), hei.ravel(), scale_mode='none', scale_factor=0.2)
#  #create the mesh
#  mesh=mlab.pipeline.delaunay2d(pts)
#  #visualize the mesh
#  surf=mlab.pipeline.surf(mesh)
#  
#  mlab.show()

  #do not quit the program until enter
  print "Press ENTER to quit."
  pl.ginput(n=10000, timeout=0, mouse_add=3, mouse_pop=1)
  
if __name__ == "__main__":
    sys.exit(main())