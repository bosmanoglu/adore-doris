import numpy as N

def earth_radius(latitude, ellipsoid='WGS84', a=None, b=None):
    """earth_radius(latitude, ellipsoid='WGS84', a=None, b=None)
    latitude: latitude of the point for calculating the local radius
    ellipsoid: WGS84 or GRS80 
    a: overwrites the ellipsoid parameters (Semi-major axis)
    c: overwrites the ellipsoid parameters (Semi-minor axis)
    """
    ell=dict( {'WGS84': (6378137.0, 6356752.314245),
               'GRS80': (6378137.0, 6356752.314140)});
    if a is None:
        a=ell[ellipsoid][0]
        b=ell[ellipsoid][1]
        
    return ((N.cos(latitude)/a)**2. + (N.sin(latitude)/b)**2. )**(-1./2.)
    
