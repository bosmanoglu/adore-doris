# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 14:27:35 2011

lon,lat=ps2ll(x,y)
x,y=ll2ps(lon,lat)
@author: bosmanoglu
"""

import pyproj
p=pyproj.Proj('+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')

def ps2ll(x,y):
    #if z==None:
    #    z=zeros(x.shape);
    lon,lat=p(x,y, inverse=True);
    return (lon,lat)
    
def ll2ps(lon,lat,):
    #if z==None:
    #    z=zeros(lon.shape);
    return p(lon,lat);    

#from osgeo import gdalnumeric 
#from osgeo import osr
#from osgeo import gdal 
#from osgeo.gdal_array import * 
#from osgeo.gdalconst import * 
#
#old_cs=osr.SpatialReference()
##from: http://spatialreference.org/ref/epsg/3031/
#ps_wkt="""
#PROJCS["WGS 84 / Antarctic Polar Stereographic",
#GEOGCS["WGS 84",
#    DATUM["WGS_1984",
#        SPHEROID["WGS 84",6378137,298.257223563,
#            AUTHORITY["EPSG","7030"]],
#        AUTHORITY["EPSG","6326"]],
#    PRIMEM["Greenwich",0,
#        AUTHORITY["EPSG","8901"]],
#    UNIT["degree",0.01745329251994328,
#        AUTHORITY["EPSG","9122"]],
#    AUTHORITY["EPSG","4326"]],
#UNIT["metre",1,
#    AUTHORITY["EPSG","9001"]],
#PROJECTION["Polar_Stereographic"],
#PARAMETER["latitude_of_origin",-71],
#PARAMETER["central_meridian",0],
#PARAMETER["scale_factor",1],
#PARAMETER["false_easting",0],
#PARAMETER["false_northing",0],
#AUTHORITY["EPSG","3031"],
#AXIS["Easting",UNKNOWN],
#AXIS["Northing",UNKNOWN]]    
#   """ 
#old_cs.ImportFromWkt(ps_wkt)
## create the new coordinate system
#wgs84_wkt = """
#GEOGCS["WGS 84",
#    DATUM["WGS_1984",
#        SPHEROID["WGS 84",6378137,298.257223563,
#            AUTHORITY["EPSG","7030"]],
#        AUTHORITY["EPSG","6326"]],
#    PRIMEM["Greenwich",0,
#        AUTHORITY["EPSG","8901"]],
#    UNIT["degree",0.01745329251994328,
#        AUTHORITY["EPSG","9122"]],
#    AUTHORITY["EPSG","4326"]]"""
#new_cs = osr.SpatialReference()
#new_cs .ImportFromWkt(wgs84_wkt)
#
#def ll2ps(lon,lat,z=0):
#    transform = osr.CoordinateTransformation(new_cs,old_cs) 
#    return transform.TransformPoint(lon,lat,z);
#
#def ps2ll(x,y,z=0):
#    transform = osr.CoordinateTransformation(old_cs,new_cs) 
#    return transform.TransformPoint(x,y,z)