from osgeo import gdalnumeric 
from osgeo import osr
from osgeo import gdal 
from osgeo.gdal_array import * 
from osgeo.gdalconst import * 
from PIL import Image
import pylab as P
import os
N=P.np


def readData(filename, ndtype=N.float64):
    '''
    z=readData('/path/to/file')
    '''
    return LoadFile(filename).astype(ndtype);
    
def writeTiff(ary, coord, filename='kgiAlos.tif', rescale=None, dataformat=gdal.GDT_Float64,lon=None, lat=None, nodata=None, grid=None, srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'):
    '''writeTiff(ary, geoTransform, filename='kgiAlos.tif', rescale=None, format=gdal.GDT_Float64 ,lon=None, lat=None):
    ary: 2D array.
    geoTransform: [top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution]
    rescale: [min max]: If given rescale ary values between min and max.
    grid: Gridding (interpolation) method None, 'nearest', 'linear', or 'cubic'. Default None.  
    If lon lat is specified set coord to None
    
    '''
       
    if coord is None:
        import scipy
        import scipy.linalg
        s=[sk/10 for sk in ary.shape]
        ary10=ary[::s[0],::s[1]];
        lon10=lon[::s[0],::s[1]];        
        lat10=lat[::s[0],::s[1]];
        #P.figure()
        #P.scatter(lon10.ravel(), lat10.ravel(), 5, ary10.ravel(), edgecolors='none')
        A=N.ones([N.multiply(*ary10.shape),3])
        line,pixel=N.meshgrid(N.r_[0:ary.shape[0]:s[0]],N.r_[0:ary.shape[1]:s[1]])
        A[:,1]=pixel.ravel()
        A[:,2]=line.ravel()
        xlon=N.dot(scipy.linalg.pinv(A), lon10.ravel())
        xlat=N.dot(scipy.linalg.pinv(A), lat10.ravel())
        ##check flip flop
        #if xlon[1]<0: #flip lr
        #    ary=N.fliplr(ary)
        #     
        #if xlat[2]>0: #flip ud
        #    ary=N.flipud(ary)    
        coord=[xlon[0],xlon[2], xlon[1], xlat[0], xlat[2], xlat[1]];
        print(coord)
        #x=lon[0,0]
        #y=lat[0,0]
        #dx=lon[0,1]-lon[0,0]
        #dy=lat[1,0]-lat[0,0]
        #xrot=0.
        #yrot=0.
        #coord=[x,dx, xrot, y,yrot, dy]

        if grid is not None:
            import scipy.interpolate
            LON,LAT=N.meshgrid(N.r_[lon.min():lon.max():abs(coord[1])], N.r_[lat.max():lat.min():-abs(coord[5])])    
            #ary=P.griddata(lon.ravel(),lat.ravel(),ary.ravel(),LON,LAT);
            ary=scipy.interpolate.griddata(N.array([lon.ravel(),lat.ravel()]).T,ary.ravel(),(LON,LAT), method=grid, fill_value=nodata);
            coord=[LON[0,0],abs(coord[1]), 0, LAT[0,0], 0,-abs(coord[5])];            
            print(coord)
                   
    if rescale:
        import basic
        ary=basic.rescale(ary, rescale);
    
    # data exists in 'ary' with values range 0 - 255
    # Uncomment next line if ary[0][0] is upper-left corner
    #ary = numpy.flipup(ary)
    Ny, Nx = ary.shape
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(filename, Nx, Ny, 1, gdal.GDT_Float64)

    #ds.SetGeoTransform( ... ) # define GeoTransform tuple
    # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    ds.SetGeoTransform( coord )    
    srs=osr.SpatialReference()
    if os.path.isfile(srs_proj4):
      srs.ImportFromWkt(open(srs_proj4).read());
    else:
      srs.ImportFromProj4(srs_proj4)
    
    ds.SetProjection(srs.ExportToWkt() );
    if nodata is not None:
        ds.GetRasterBand(1).SetNoDataValue(nodata);
    ds.GetRasterBand(1).WriteArray(ary)
    ds = None
    print("File written to: " + filename)

def writeAny(ary, coord, fileformat="GTiff", filename='kgiAlos.tif', rescale=None, dataformat=gdal.GDT_Float64,lon=None, lat=None, nodata=None, grid=False, srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'):
    '''writeAny(ary, geoTransform, format="GTiff", filename='kgiAlos.tif', rescale=None, datatype=gdal.GDT_Float64 ,lon=None, lat=None):
    ary: 2D array.
    geoTransform: [top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution]
    fileformat: "GTiff" 
    rescale: [min max]: If given rescale ary values between min and max.
    
    
    If lon lat is specified set coord to None
    
    '''
       
    if coord is None:
        import scipy
        import scipy.linalg
        s=[sk/10 for sk in ary.shape]
        ary10=ary[::s[0],::s[1]];
        lon10=lon[::s[0],::s[1]];        
        lat10=lat[::s[0],::s[1]];
        #P.figure()
        #P.scatter(lon10.ravel(), lat10.ravel(), 5, ary10.ravel(), edgecolors='none')
        A=N.ones([N.multiply(*ary10.shape),3])
        line,pixel=N.meshgrid(N.r_[0:ary.shape[0]:s[0]],N.r_[0:ary.shape[1]:s[1]])
        A[:,1]=pixel.ravel()
        A[:,2]=line.ravel()
        xlon=N.dot(scipy.linalg.pinv(A), lon10.ravel())
        xlat=N.dot(scipy.linalg.pinv(A), lat10.ravel())
        ##check flip flop
        #if xlon[1]<0: #flip lr
        #    ary=N.fliplr(ary)
        #     
        #if xlat[2]>0: #flip ud
        #    ary=N.flipud(ary)    
        coord=[xlon[0],xlon[2], xlon[1], xlat[0], xlat[2], xlat[1]];
        print(coord)
        #x=lon[0,0]
        #y=lat[0,0]
        #dx=lon[0,1]-lon[0,0]
        #dy=lat[1,0]-lat[0,0]
        #xrot=0.
        #yrot=0.
        #coord=[x,dx, xrot, y,yrot, dy]

        if grid:
            import scipy.interpolate
            LON,LAT=N.meshgrid(N.r_[lon.min():lon.max():abs(coord[1])], N.r_[lat.max():lat.min():-abs(coord[5])])    
            #ary=P.griddata(lon.ravel(),lat.ravel(),ary.ravel(),LON,LAT);
            ary=scipy.interpolate.griddata(N.array([lon.ravel(),lat.ravel()]).T,ary.ravel(),(LON,LAT), method='cubic');
            coord=[LON[0,0],abs(coord[1]), 0, LAT[0,0], 0,-abs(coord[5])];            
            print(coord)
                   
    if rescale:
        import basic
        ary=basic.rescale(ary, rescale);
    
    # data exists in 'ary' with values range 0 - 255
    # Uncomment next line if ary[0][0] is upper-left corner
    #ary = numpy.flipup(ary)
    Ny, Nx = ary.shape
    driver = gdal.GetDriverByName(fileformat)
    ds = driver.Create(filename, Nx, Ny, 1, dataformat)

    #ds.SetGeoTransform( ... ) # define GeoTransform tuple
    # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    ds.SetGeoTransform( coord )    
    srs=osr.SpatialReference()
    srs.ImportFromProj4(srs_proj4)
    ds.SetProjection(srs.ExportToWkt() );
    if nodata is not None:
        ds.GetRasterBand(1).SetNoDataValue(0);
    ds.GetRasterBand(1).WriteArray(ary)
    ds = None
    print("File written to: " + filename)


def writeCSV(ary, filename='kgiAlos.tif', rescale=None, dataformat="%f", lon=None, lat=None, nodata=None, grid=False, srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'):
    '''writeAny(ary, geoTransform, format="GTiff", filename='kgiAlos.tif', rescale=None, format=gdal.GDT_Float64 ,lon=None, lat=None):
    ary: 2D array.
    geoTransform: [top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution]
    format: "GTiff" 
    rescale: [min max]: If given rescale ary values between min and max.
    
    If lon lat is specified set coord to None
    
    '''
       
    if coord is None:
        import scipy
        import scipy.linalg
        s=[sk/10 for sk in ary.shape]
        ary10=ary[::s[0],::s[1]];
        lon10=lon[::s[0],::s[1]];        
        lat10=lat[::s[0],::s[1]];
        #P.figure()
        #P.scatter(lon10.ravel(), lat10.ravel(), 5, ary10.ravel(), edgecolors='none')
        A=N.ones([N.multiply(*ary10.shape),3])
        line,pixel=N.meshgrid(N.r_[0:ary.shape[0]:s[0]],N.r_[0:ary.shape[1]:s[1]])
        A[:,1]=pixel.ravel()
        A[:,2]=line.ravel()
        xlon=N.dot(scipy.linalg.pinv(A), lon10.ravel())
        xlat=N.dot(scipy.linalg.pinv(A), lat10.ravel())
        ##check flip flop
        #if xlon[1]<0: #flip lr
        #    ary=N.fliplr(ary)
        #     
        #if xlat[2]>0: #flip ud
        #    ary=N.flipud(ary)    
        coord=[xlon[0],xlon[2], xlon[1], xlat[0], xlat[2], xlat[1]];
        print(coord)
        #x=lon[0,0]
        #y=lat[0,0]
        #dx=lon[0,1]-lon[0,0]
        #dy=lat[1,0]-lat[0,0]
        #xrot=0.
        #yrot=0.
        #coord=[x,dx, xrot, y,yrot, dy]

        if grid:
            import scipy.interpolate
            LON,LAT=N.meshgrid(N.r_[lon.min():lon.max():abs(coord[1])], N.r_[lat.max():lat.min():-abs(coord[5])])    
            #ary=P.griddata(lon.ravel(),lat.ravel(),ary.ravel(),LON,LAT);
            ary=scipy.interpolate.griddata(N.array([lon.ravel(),lat.ravel()]).T,ary.ravel(),(LON,LAT), method='cubic');
            coord=[LON[0,0],abs(coord[1]), 0, LAT[0,0], 0,-abs(coord[5])];            
            print(coord)
                   
    if rescale:
        import basic
        ary=basic.rescale(ary, rescale);
    
    # data exists in 'ary' with values range 0 - 255
    # Uncomment next line if ary[0][0] is upper-left corner
    #ary = numpy.flipup(ary)
    Ny, Nx = ary.shape
    item_length=Ny*Nx
    
    import csv
    lol=[lon.ravel(), lat.ravel(), ary.ravel()]
    with open(filename, 'wb') as test_file:
        file_writer = csv.writer(test_file)
        for i in range(item_length):
            file_writer.writerow([x[i] for x in lol])
    print("File written to: " + filename)


    
def readCoord(filename, srs_proj4=None, dtype=N.float64):
    '''
    lon,lat=lonlat('/path/to/file', srs_proj4=None)
    '''
    #http://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
    # get the existing coordinate system
    xn,yn,xN,yN=corners(filename);
    
    ds = gdal.Open(filename)
    if srs_proj4 is None:
        old_cs=osr.SpatialReference()
        old_cs.ImportFromWkt(ds.GetProjectionRef())
    else:
        old_cs=osr.SpatialReference()
        old_cs.ImportFromProj4(srs_proj4);
        
    # create the new coordinate system
    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]"""
    new_cs = osr.SpatialReference()
    new_cs .ImportFromWkt(wgs84_wkt)
    # create a transform object to convert between coordinate systems
    transform = osr.CoordinateTransformation(old_cs,new_cs) 
    
    #get the point to transform, pixel (0,0) in this case
    #width = ds.RasterXSize
    #height = ds.RasterYSize
    #gt = ds.GetGeoTransform()
    #minx = gt[0]
    #miny = gt[3] + width*gt[4] + height*gt[5] 
    
    #get the coordinates in lat long
    #latlong = transform.TransformPoint(minx,miny)     
    lonn,latn,z=transform.TransformPoint(xn,yn)
   # print latn, lonn
    #lonN,latn,z=transform.TransformPoint(xN,yn)
    lonN,latN,z=transform.TransformPoint(xN,yN)
    lat=N.linspace(latn,latN,ds.RasterYSize).astype(dtype);
    lon=N.linspace(lonn,lonN,ds.RasterXSize).astype(dtype);
    LON,LAT=N.meshgrid(lon,lat);    
    return LON, N.flipud(LAT);      

def corners(filename):
    '''
    (minx,miny,maxx,maxy)=corners('/path/to/file')
    '''
    #http://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
    ds = gdal.Open(filename)
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5] 
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3] 
    return (minx,miny,maxx,maxy) 
    
def getGeoTransform(filename):
    '''
    [top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution]=getGeoTransform('/path/to/file')
    '''
    #http://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
    ds = gdal.Open(filename)
    return ds.GetGeoTransform()
    
def transformPoint(x,y,z,s_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', t_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'):
    '''
    transformPoint(x,y,z,s_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', t_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    
    Known Bugs: gdal transform may fail if a proj4 string can not be found for the EPSG or WKT formats. 
    '''
    srs_cs=osr.SpatialReference()    
    if "EPSG" == s_srs[0:4]:    
      srs_cs.ImportFromEPSG(int(s_srs.split(':')[1]));
    elif "GEOCCS" == s_srs[0:6]:
      srs_cs.ImportFromWkt(s_srs);
    else:
      srs_cs.ImportFromProj4(s_srs);

    trs_cs=osr.SpatialReference()    
    if "EPSG" == t_srs[0:4]:    
      trs_cs.ImportFromEPSG(int(t_srs.split(':')[1]));
    elif "GEOCCS" == t_srs[0:6]:
      trs_cs.ImportFromWkt(t_srs);
    else:
      trs_cs.ImportFromProj4(t_srs);

    transform = osr.CoordinateTransformation(srs_cs,trs_cs) 
    try:
      return transform.TransformPoint((x,y,z));
    except:
      return transform.TransformPoint(x,y,z);
    
      
    
