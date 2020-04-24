from osgeo import gdalnumeric 
from osgeo import osr
from osgeo import gdal 
from osgeo.gdal_array import * 
from osgeo.gdalconst import * 
from PIL import Image
import pylab as P
import os
import numpy as np
from IPython.core.debugger import set_trace

def readData(filename, ndtype=np.float64):
    '''
    z=readData('/path/to/file')
    '''
    if os.path.isfile(filename):
      return LoadFile(filename).astype(ndtype);
    else:
      return gdal.Open(filename, gdal.GA_ReadOnly).readAsArray()

    
def writeTiff(ary, coord, filename='kgiAlos.tif', rescale=None, format=gdal.GDT_Float64,lon=None, lat=None, nodata=None, grid=False, cog=False, srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', options=[], gcps=None):
    '''writeTiff(ary, geoTransform, filename='kgiAlos.tif', rescale=None, format=gdal.GDT_Float64 ,lon=None, lat=None):
    ary: 2D array.
    geoTransform: [top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution]
    rescale: [min max]: If given rescale ary values between min and max.
    
    If lon lat is specified set coord to None
    
    '''
       
    if coord is None and gcps is None:
        import scipy
        import scipy.linalg
        s=[sk//10 for sk in ary.shape]
        ary10=ary[::s[0],::s[1]];
        lon10=lon[::s[0],::s[1]];        
        lat10=lat[::s[0],::s[1]];
        #P.figure()
        #P.scatter(lon10.ravel(), lat10.ravel(), 5, ary10.ravel(), edgecolors='none')
        A=np.ones([np.multiply(*ary10.shape),3])
        line,pixel=np.meshgrid(np.r_[0:ary.shape[0]:s[0]],np.r_[0:ary.shape[1]:s[1]])
        A[:,1]=pixel.ravel()
        A[:,2]=line.ravel()
        xlon=np.dot(scipy.linalg.pinv(A), lon10.ravel())
        xlat=np.dot(scipy.linalg.pinv(A), lat10.ravel())
        ##check flip flop
        #if xlon[1]<0: #flip lr
        #    ary=np.fliplr(ary)
        #     
        #if xlat[2]>0: #flip ud
        #    ary=np.flipud(ary)    
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
            LON,LAT=np.meshgrid(np.r_[lon.min():lon.max():abs(coord[1])], np.r_[lat.max():lat.min():-abs(coord[5])])    
            #ary=P.griddata(lon.ravel(),lat.ravel(),ary.ravel(),LON,LAT);
            ary=scipy.interpolate.griddata(np.array([lon.ravel(),lat.ravel()]).T,ary.ravel(),(LON,LAT), method='cubic');
            coord=[LON[0,0],abs(coord[1]), 0, LAT[0,0], 0,-abs(coord[5])];            
            print(coord)
                   
    if rescale:
        import basic
        ary=basic.rescale(ary, rescale);
    
    # data exists in 'ary' with values range 0 - 255
    # Uncomment next line if ary[0][0] is upper-left corner
    #ary = numpy.flipup(ary)
    if ary.ndim==2:
      Ny, Nx = ary.shape
      Nb=1;
      #ds = driver.Create(filename, Nx, Ny, 1, gdal.GDT_Float64)
    elif ary.ndim==3:
      Ny,Nx,Nb = ary.shape #Nb: number of bands. #osgeo.gdal expects, (band, row, col), so this is a deviation from that. 
    else:
      print("Input array has to be 2D or 3D.")
      return None
    driver = gdal.GetDriverByName("GTiff")
    if cog:
      options = ["TILED=YES","COMPRESS=LZW","INTERLEAVE=BAND","BIGTIFF=YES"]
    ds = driver.Create(filename, Nx, Ny, Nb, gdal.GDT_Float64, options)
      
    srs=osr.SpatialReference()
    srs.ImportFromProj4(srs_proj4)
    ds.SetProjection(srs.ExportToWkt() );
    #ds.SetGeoTransform( ... ) # define GeoTransform tuple
    # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    if gcps is None:
      ds.SetGeoTransform( coord )    
    else:
      if type(gcps[0])== gdal.GCP:
        ds.SetGCPs(gcps, srs.ExportToWkt())
      elif type(gcps[0])==np.int and len(gcps)==2 and lat is not None:
        gcps_list=create_gcp_list(lon,lat,np.zeros(lat.shape), gcp_count=[gcps[0], gcps[1]])
        ds.SetGCPs(gcp_list, srs.ExportToWkt())
      else:
        print('unsupported type of GCPs. Skipping.')
    if nodata is not None:
        ds.GetRasterBand(1).SetNoDataValue(nodata);
    if Nb==1:
      ds.GetRasterBand(1).WriteArray(ary)
    else:
      for b in range(Nb):
        ds.GetRasterBand(b+1).WriteArray(ary[:,:,b])
    # optimize for COG	
    if cog:
      ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64, 128, 256])

    ds = None
    print("File written to: " + filename);

def create_gcp_list(x,y,z,p=None, l=None,gcp_count=[2,2]):
    """create_gcp_list(x,y,z,p=None, l=None, gcp_count=[2,2])
    if xyz is in the same shape as image, uses gcp count to select a reasonable amount of gcps. 
    if xyz is not in the same shape as image, p and l need to be provided to select the correct pixel and line. 
    """
    gcp_list=[]
    if l is None or p is None:
      p=np.linspace(0,x.shape[0]-1, gcp_count[0]).astype(int)
      l=np.linspace(0,x.shape[1]-1, gcp_count[1]).astype(int)
      for pp in p:
        for ll in l:
          gcp=gdal.GCP(x[pp,ll], y[pp,ll], z[pp,ll], float(pp), float(ll))
          gcp_list.append(gcp)
    else:
      p=p.ravel().astype(float)
      l=l.ravel().astype(float)
      x=x.ravel()
      y=y.ravel()
      z=z.ravel()
      for k in range(l.size):
        gcp=gdal.GCP(x[k], y[k], z[k], p[k], l[k])
        gcp_list.append(gcp)
    return gcp_list 

def writeAny(ary, coord, fileformat="GTiff", filename='kgiAlos.tif', rescale=None, format=gdal.GDT_Float64,lon=None, lat=None, nodata=None, grid=False, srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'):
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
        s=[sk//10 for sk in ary.shape]#BRANDON EDIT FOR COMPATIBILITY: changed / to // for python 3
         
        ary10=ary[::s[0],::s[1]];
        lon10=lon[::s[0],::s[1]];        
        lat10=lat[::s[0],::s[1]];
        #P.figure()
        #P.scatter(lon10.ravel(), lat10.ravel(), 5, ary10.ravel(), edgecolors='none')
        A=np.ones([np.multiply(*ary10.shape),3])
        line,pixel=np.meshgrid(np.r_[0:ary.shape[0]:s[0]],np.r_[0:ary.shape[1]:s[1]])
        A[:,1]=pixel.ravel()
        A[:,2]=line.ravel()
        xlon=np.dot(scipy.linalg.pinv(A), lon10.ravel())
        xlat=np.dot(scipy.linalg.pinv(A), lat10.ravel())
        ##check flip flop
        #if xlon[1]<0: #flip lr
        #    ary=np.fliplr(ary)
        #     
        #if xlat[2]>0: #flip ud
        #    ary=np.flipud(ary)    
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
            LON,LAT=np.meshgrid(np.r_[lon.min():lon.max():abs(coord[1])], np.r_[lat.max():lat.min():-abs(coord[5])])    
            #ary=P.griddata(lon.ravel(),lat.ravel(),ary.ravel(),LON,LAT);
            ary=scipy.interpolate.griddata(np.array([lon.ravel(),lat.ravel()]).T,ary.ravel(),(LON,LAT), method='cubic');
            coord=[LON[0,0],abs(coord[1]), 0, LAT[0,0], 0,-abs(coord[5])];            
            print(coord)
                   
    if rescale:
        import basic
        ary=basic.rescale(ary, rescale);
    
    # data exists in 'ary' with values range 0 - 255
    # Uncomment next line if ary[0][0] is upper-left corner
    #ary = numpy.flipup(ary)
    if ary.ndim ==2:
      Ny, Nx = ary.shape
      Nb = 1;
    elif ary.ndim==3:
      Ny,Nx,Nb=ary.shape
    else: 
      print("Input array has to be 2D or 3D.")
      return None
    
    driver = gdal.GetDriverByName(fileformat)
    ds = driver.Create(filename, Nx, Ny, Nb, gdal.GDT_Float64)

    #ds.SetGeoTransform( ... ) # define GeoTransform tuple
    # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    ds.SetGeoTransform( coord )    
    srs=osr.SpatialReference()
    srs.ImportFromProj4(srs_proj4)
    ds.SetProjection(srs.ExportToWkt() );
    if nodata is not None:
        ds.GetRasterBand(1).SetNoDataValue(0);
    if Nb==1:
      ds.GetRasterBand(1).WriteArray(ary)
    else:
      for b in range(Nb):
        ds.GetRasterBand(b+1).WriteArray(ary[:,:,b])
    ds = None
    print("File written to: " + filename);


def writeCSV(ary, filename='gis_file.csv', geotransform=None, rescale=None, format="%f", lon=None, lat=None, nodata=None, grid=False, srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'):
    '''writeCSV(ary, geoTransform=None, format="GTiff", filename='gis_file.csv', rescale=None, format="%f" ,lon=None, lat=None):
    ary: 2D array.
    geoTransform: [top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution]
    format: "GTiff" 
    rescale: [min max]: If given rescale ary values between min and max.
    
    '''
       
    if geotransform is None:
        import scipy
        import scipy.linalg
        s=[sk//10 for sk in ary.shape]
        ary10=ary[::s[0],::s[1]];
        lon10=lon[::s[0],::s[1]];        
        lat10=lat[::s[0],::s[1]];
        #P.figure()
        #P.scatter(lon10.ravel(), lat10.ravel(), 5, ary10.ravel(), edgecolors='none')
        A=np.ones([np.multiply(*ary10.shape),3])
        line,pixel=np.meshgrid(np.r_[0:ary.shape[0]:s[0]],np.r_[0:ary.shape[1]:s[1]])
        A[:,1]=pixel.ravel()
        A[:,2]=line.ravel()
        xlon=np.dot(scipy.linalg.pinv(A), lon10.ravel())
        xlat=np.dot(scipy.linalg.pinv(A), lat10.ravel())
        ##check flip flop
        #if xlon[1]<0: #flip lr
        #    ary=np.fliplr(ary)
        #     
        #if xlat[2]>0: #flip ud
        #    ary=np.flipud(ary)    
        geotransform=[xlon[0],xlon[2], xlon[1], xlat[0], xlat[2], xlat[1]];
        print(geotransform)
        #x=lon[0,0]
        #y=lat[0,0]
        #dx=lon[0,1]-lon[0,0]
        #dy=lat[1,0]-lat[0,0]
        #xrot=0.
        #yrot=0.
        #coord=[x,dx, xrot, y,yrot, dy]

        if grid:
            import scipy.interpolate
            LON,LAT=np.meshgrid(np.r_[lon.min():lon.max():abs(coord[1])], np.r_[lat.max():lat.min():-abs(coord[5])])    
            #ary=P.griddata(lon.ravel(),lat.ravel(),ary.ravel(),LON,LAT);
            ary=scipy.interpolate.griddata(np.array([lon.ravel(),lat.ravel()]).T,ary.ravel(),(LON,LAT), method='cubic');
            geotransform=[LON[0,0],abs(coord[1]), 0, LAT[0,0], 0,-abs(coord[5])];            
            print(geotransform)
    else:
      y = np.linspace(1, ary.shape[0], ary.shape[0])
      x = np.linspace(1, ary.shape[1], ary.shape[1])
      Y,X=np.meshgrid(y,x ,indexing='ij')
      lon=geotransform[0]+geotransform[1]*X+Y*geotransform[2]
      lat=geotransform[3]+geotransform[4]*X+Y*geotransform[5]
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
    print("File written to: " + filename);


    
def readCoord(filename, srs_proj4=None, dtype=np.float64):
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
   # print(latn, lon)
    #lonN,latn,z=transform.TransformPoint(xN,yn)
    lonN,latN,z=transform.TransformPoint(xN,yN)
    lat=np.linspace(latn,latN,ds.RasterYSize).astype(dtype);
    lon=np.linspace(lonn,lonN,ds.RasterXSize).astype(dtype);
    LON,LAT=np.meshgrid(lon,lat);    
    return LON, np.flipud(LAT);      

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

def bounding_box(filename):
    """
    ((lon1,lat1), (lon2,lat2), (lon3,lat3), (lon4,lat4))=bounding_box('/path/to/file')
    """
    gT=getGeoTransform(filename)
    width, height=get_size(filename)     
    return (xy2coord(0,0,gT), xy2coord(width,0,gT), xy2coord(width, height,gT), xy2coord(0, height,gT))


def xy2coord(x,y,gT):
    '''
    lon,lat=xy2coord(x,y,geoTransform)
    projects pixel index to position based on geotransform.
    '''
    coord_x=gT[0] + x*gT[1] + y*gT[2]
    coord_y=gT[3] + x*gT[4] + y*gT[5]
    return coord_x, coord_y

def coord2xy(x,y,gT):
    '''
    x,y = coord2xy(lon, lat, geoTransform)
    calculates pixel index closest to the lon, lat.
    '''
    #ref: https://gis.stackexchange.com/questions/221292/retrieve-pixel-value-with-geographic-coordinate-as-input-with-gdal/221430
    xOrigin = gT[0]
    yOrigin = gT[3]
    pixelWidth = gT[1]
    pixelHeight = -gT[5]
    
    col = np.array((x - xOrigin) / pixelWidth).astype(int)
    row = np.array((yOrigin - y) / pixelHeight).astype(int)
    
    return row,col    
    
def getGeoTransform(filename):
    '''
    [top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution]=getGeoTransform('/path/to/file')
    '''
    #http://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file
    ds = gdal.Open(filename)
    return ds.GetGeoTransform()
def get_size(filename):
    """(width, height) = get_size(filename)
    """
    ds = gdal.Open(filename)
    width = ds.RasterXSize
    height = ds.RasterYSize
    ds=None
    return (width, height)

def get_proj4(filename):
    ds=gdal.Open(filename)
    sr=gdal.osr.SpatialReference()
    sr.ImportFromWkt(ds.GetProjectionRef)
    return sr.ExportToProj4()

def transformPoint(x,y,z,s_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', t_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'):
    '''
    transformPoint(x,y,z,s_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', t_srs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    
    Known Bugs: gdal transform may fail if a proj4 string can not be found for the EPSG or WKT formats. 
    '''
    from .. import base
    
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
    
    if base.numel(x)>1:
      return [  transformPoint(x[k], y[k], z[k]) for k in range(base.numel(x))]
    else:
      try:
        return transform.TransformPoint((x,y,z));
      except: 
        return transform.TransformPoint(x,y,z)
    
def rsat2_export(filename, export_filename=None, yclip=225):
    """ 'export_filename'=rsat2_export(filename, export_filename=None, yclip=225)
    """
    ds=gdal.Open(filename, gdal.GA_ReadOnly)
    w=ds.RasterXSize
    h=ds.RasterYSize
    data=10.*np.log10(abs(ds.ReadAsArray(ysize=ds.RasterYSize-yclip)))    
    gT=ds.GetGeoTransform()
    if export_filename is None:
      timestr=''.join(ds.GetMetadata()['ACQUISITION_START_TIME'].split(".")[0].split(":"))
      export_filename='_'.join(filename.split(":")[0:2])+"_"+timestr+"_cog.tif"
    data[data==-np.inf]=np.nan
    data[data==np.inf]=np.nan #should not be necessary
    writeTiff(data, gT, filename=export_filename, cog=True, gcps=ds.GetGCPs(), nodata=np.nan)    
    return export_filename 

def clip_gT(gT, xmin, xmax, ymin, ymax, method='image'):
    '''calculate new geotransform for a clipped raster either using pixels or projected coordinates.
    clipped_gT=clip_gT(gT, xmin, xmax, ymin, ymax, method='image')
    method: 'image' | 'coord'    
    '''
    if method == 'image':
      y,x=xy2coord(ymin, xmin, gT); #top left, reference, coordinate
    if method == 'coord':
      #find nearest pixel
      yi, xi = coord2xy(ymin, xmin, gT)
      #get pixel coordinate
      y,x=xy2coord(yi, xi, gT)
    gTc=list(gT)
    gTc[0]=y
    gTc[3]=x
    return tuple(gTc)

def auto_clip(arr, gT, no_data=np.nan):
    """automatically  remova the excess no-data pixels in raster. Similar to auto_clip in GIMP.
    cliipped_raster, clipped_gT = auto_clip(raster, geoTransform, no_data=np.nan)
    """
    if np.isnan(no_data):
      m=~np.isnan(arr)
    else:
      m= arr!=no_data
    data_cols = numpy.where(m.sum(0)  > 50)[0]    
    data_rows = numpy.where(m.sum(1)  > 50)[0]
    gTc=clip_gT(gT, data_rows[0], data_rows[-1], data_cols[0], data_cols[-1])
    arrC=arr[data_rows[0]:data_rows[-1], data_cols[0]:data_cols[-1]]
    return arrC, gTc 

def translate_gT(gT, x_offset, y_offset):
    '''gT_translated=translate_gT(gT, x_offset, y_offset)
    simply offsets the starting 0th and 3rd elements of geotransform accordingly. 
    '''
    gTt=list(gT)
    gTt[0]=gTt[0]+x_offset
    gTt[3]=gTt[3]+y_offset
    return tuple(gTt)

def translate_tif(filename, x_offset, y_offset):
    arr=readData(filename)
    gT=getGeoTransform(filename)
    gTt=gsp.connectors.gdal.translate_gT(gT, x_offset, y_offset)
    writeTiff(arr, gTt, filename=filename[-4]+'_translated.tif')
    return filename[:-4]+'_translated.tif'

def auto_clip_tif(f, no_data=np.nan):
    print('Reading {}'.format(f))
    arr=readData(f)
    gT=getGeoTransform(f)
    if np.isnan(no_data):
      m=~np.isnan(arr)
    else:
      m= arr!=no_data
    data_cols = numpy.where(m.sum(0)  > 50)[0]
    data_rows = numpy.where(m.sum(1)  > 50)[0]
    gTc=clip_gT(gT, data_rows[0], data_rows[-1], data_cols[0], data_cols[-1])
    arrC=arr[data_rows[0]:data_rows[-1], data_cols[0]:data_cols[-1]]
    writeTiff(arrC, gTc, filename=f[:-4]+'_clipped.tif')

def distance_lat_lon(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - np.cos((lat2-lat1)*p)/2 + np.cos(lat1*p)*np.cos(lat2*p) * (1-np.cos((lon2-lon1)*p)) / 2
    return 12742 * np.arcsin(np.sqrt(a))

def closest_lat_lon(lat_vector, lon_vector, lat_point, lon_point):
    """
     Find the closest index in a vector.
     index = closest_lat_lon(lat_vector, lon_vector, lat_point, lon_point)
    """
    return np.argmin(distance_lat_lon(lat_vector, lon_vector,lat_point,lon_point))
def get_point_value(filename, x,y,srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs', band=1):
    """
    z=get_point_value(filename, x,y,srs_proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    """
    ds=gdal.Open(filename, gdal.GA_ReadOnly)
    w=ds.RasterXSize
    h=ds.RasterYSize
    gT=ds.GetGeoTransform()
    t_srs=get_proj4(filename)
    rb=ds.GetRasterBand(band)
    if t_srs != srs_proj4:
      x,y,z=transformPoint(x,y,z,s_srs=srs_proj4, t_srs=t_srs)
    cx,cy=coord2xy(x,y,gT)
    return rb.ReadAsArray(px,py,1,1)[0]
