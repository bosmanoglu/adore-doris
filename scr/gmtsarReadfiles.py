#!/usr/bin/env python
"""
gmtsarReadfiles.py SlcFile.SLC ParameterFile.PRM StateVectorFile.LED
"""
import os, sys
import getopt
import StringIO
import ConfigParser
import matplotlib
import matplotlib.pylab
import numpy as np
from scipy import interpolate
import adore
import gis

def usage():
    print __doc__

def usageLong():
    print """
  DESCRIPTION [default]:
    """
    
def main(argv):
    if not argv:
        usage()
        sys.exit(2)
    try:
        slcfile=argv[0];
    except:
        print "SLC (*.DAT) file not specified."
        sys.exit(2)
    try:
        prmfile=argv[1];
    except:
        print "Parameter (*.PRM) file not specified."
        sys.exit(2)
    try:
        ledfile=argv[2];
    except:
        print "Leader (*.LED) file not specified."
        sys.exit(2)
    if not os.path.exists(prmfile):
	print "File not found:", prmfile
	sys.exit(2)
    if not os.path.exists(ledfile):
	print "File not found:", ledfile
	sys.exit(2)
    if not os.path.exists(slcfile):
	print "File not found:", slcfile
	sys.exit(2)
    #print('prmfile: %s' % prmfile);    
    #print('slcfile: %s' % slcfile);    
    c=299792458; #299792231.9364096;
    #print('Reading the parameter file: %s' % prmfile);
    d=prm2dict(prmfile)
    d['slcfile']=slcfile #+'.ci2'
    d['prmfile']=prmfile
    d['product']=d['slc_file'][:-4] # NOTE this is not the input file. This is read from the prm. 
    d['dummy']  ='dummy'
    d['checknumlines'] = int(d['num_lines']); #int(d['num_patches'])*int(d['num_valid_az'])/2    
    d['calc_num_lines']=os.stat(slcfile).st_size/int(d['num_rng_bins'])/2/2;
    #print d
    if int(d['sc_identity']) <= 2 :
	d['producttype'] = "ERS"
    elif int(d['sc_identity']) == 3 :
	d['producttype'] = "ALOS"
    elif int(d['sc_identity']) == 4 :
	d['producttype'] = "ASAR"
    d['sarprocessor']='GAMMA'
    #d['pass']='dummy'#'DESCENDING'
    d['frequency']=c/np.double(d['radar_wavelength'])
    d['rng_samp_rate']=np.double(d['rng_samp_rate'])/1e6; #MHz
    d['rbw']=d['rng_samp_rate']
    dts=matplotlib.pylab.num2date(matplotlib.pylab.datestr2num(d['sc_clock_start'][:4]+'-01-01')-1+np.double(d['sc_clock_start'][4:]))
    #d['scenedate']=dt.isoformat()
    d['firstlinetime']=dts.strftime('%d-%b-%Y %H:%M:%S.')+str(dts.microsecond)
    dte=matplotlib.pylab.num2date(matplotlib.pylab.datestr2num(d['sc_clock_stop'][:4]+'-01-01')-1+np.double(d['sc_clock_stop'][4:]))
    d['lastlinetime']=dte.strftime('%d-%b-%Y %H:%M:%S.')+str(dte.microsecond)
    d['prf']=np.double(d['prf'])
    d['abw']=d['prf']
    d['twt']=(2.*np.double(d['near_range'])/c)*1e3-np.double(d['chirp_ext'])/(d['rbw']*1e6)*1e3 #ms
    d['sv']=np.loadtxt(ledfile, skiprows=1, usecols=[2,3,4,5])
    d['numstatevectors']=len(d['sv'])
    #estimate scene center
    pts=np.zeros([len(d['sv']),3]); #zeros((A.mobj.readfiles.leader_datapoints.shape[0],3))
    for k in xrange(pts.shape[0]):
      pts[k,:]=gis.transformPoint(d['sv'][k,1], d['sv'][k,2], d['sv'][k,3], s_srs="EPSG:4978"); #[0] is time. 

    #pts_m=pts.mean(0); #center orbit
    d_pts=np.diff(pts,1,0).mean(0); # speed for heading
    #find center by interpolation:
    x=d['sv'][:,0];
    cpt=np.zeros([3]); #center point
    xcenter=(dts.hour+dte.hour)*0.5*60*60+(dts.minute+dte.minute)*0.5*60+(dts.second+dte.second)*0.5;
    for k in xrange(3):
      y=d['sv'][:,k+1];
      f=interpolate.interp1d(x,y);
      cpt[k]=f(xcenter);
    pts_m=gis.transformPoint(cpt[0], cpt[1], cpt[2], s_srs="EPSG:4978"); #[0] is time. returns, lon, lat, alt.
    if d_pts[1]<0: # if latitude is decreasing...
      d['pass']='DESCENDING';
    else:
      d['pass']='ASCENDING';
    heading=90-np.rad2deg(np.arctan2(d_pts[1], d_pts[0])); #convert from x=0 to north=0. Also change + angle direction from counter clockwise to clockwise. 
    groundRangeToNearRange=np.sqrt(np.double(d['near_range'])**2-(np.double(d['sc_height']))**2.);
    groundRangeToCenter=c/(d['rbw']*1e6)/2.*int(d['num_rng_bins'])/2.;
    if d['lookdir']=="R":
      d['swath']="Right"
      lookVector=[np.cos(np.deg2rad(heading+90)), np.sin(np.deg2rad(heading+90))];
    else:
      d['swath']="Left"
      lookVector=[np.cos(np.deg2rad(heading-90)), np.sin(np.deg2rad(heading-90))];
    offsetNorth=lookVector[0]*(groundRangeToCenter+groundRangeToNearRange); #in m
    offsetEast= lookVector[1]*(groundRangeToCenter+groundRangeToNearRange); #in m
    #print('N: %f m    E: %f m' %(offsetNorth, offsetEast));
    offsetNorthDeg=offsetNorth/111e3; # in deg
    offsetEastDeg =360*offsetEast*1e-3/(2*np.pi*6356.750*np.cos(pts_m[1]/180*np.pi)); #in deg
    #print('N: %f deg    E: %f deg' %(offsetNorthDeg, offsetEastDeg));
    #print('Orbit N: %f deg    E: %f deg' %(pts_m[1], pts_m[0]));
    d['center_lat']=pts_m[1]+offsetNorthDeg;
    d['center_lon']=pts_m[0]+offsetEastDeg;
    d['heading']=heading;
    #print('Writing the Doris result file...');
    printout(d)
    #print('Converting the slc file to Doris format...');
    #convert slc file
    #bsq2bip(slcfile, int(d['num_rng_bins']));
    #print('All done.');
def prm2dict(prm):
  '''prm2dict(prm)
  '''
  #http://stackoverflow.com/questions/2885190/using-pythons-configparser-to-read-a-file-without-section-name
  prm_str = '[gmtsar]\n' + open(prm, 'r').read()
  prm_fp = StringIO.StringIO(prm_str)
  config = ConfigParser.RawConfigParser()
  config.readfp(prm_fp)
  return config._sections['gmtsar']

def printout(d):
	''' printout(dict)
	'''

        str0='''=====================================================
MASTER RESULTFILE:      master.res 

Created by:
InSAR Processor:        Doris (Delft o-o Radar Interferometric Software)
Version:                Version (optimal)
FFTW library:           used
VECLIB library:         not used
LAPACK library:         not used
Compiled at:            Dec 19 2008 17:26:52
By GNU gcc:             4.1.4
File creation at:       Fri Dec  19 19:08:21 2008

  --------------------------------------------------------
 | Delft Institute of Earth Observation and Space Systems |
 |        Delft University of Technology                  |
 |       http://enterprise.lr.tudelft.nl/doris/           |
  --------------------------------------------------------

Start_process_control
readfiles:              1
precise_orbits:         0
modify_orbits:          0
crop:                   0
sim_amplitude:          0
master_timing:          0
oversample:             0
resample:               0
filt_azi:               0
filt_range:             0
NOT_USED:               0
End_process_control

*******************************************************************
*_Start_readfiles:
*******************************************************************
Volume file: %s
Volume_ID:                                      %s
Volume_identifier:                              %s
Volume_set_identifier:                          %s
(Check)Number of records in ref. file:          %d
Product type specifier:                         %s
SAR_PROCESSOR:                                  %s
SWATH:						%s
PASS:						%s
RADAR_FREQUENCY (HZ):                           %f

Logical volume generating facility:             %s
Logical volume creation date:                   %s
Location and date/time of product creation:     %s
Scene identification:                           ORBIT %s
Scene location:                                 FRAME %s
Leader file: %s
Sensor platform mission identifer:              %s
Scene_centre_latitude:                          %.4f
Scene_centre_longitude:                         %.4f
Scene_centre_heading:				%.2f
Radar_wavelength (m):                           %f
First_pixel_azimuth_time (UTC):                 %s
TIME TO LAST LINE: compute prf:                 %s 
Pulse_Repetition_Frequency (computed, Hz):      %f
Total_azimuth_band_width (Hz):                  %f 
Weighting_azimuth:                              %s
Xtrack_f_DC_constant (Hz, early edge):          %f
Xtrack_f_DC_linear (Hz/s, early edge):          %f
Xtrack_f_DC_quadratic (Hz/s/s, early edge):     %f
Range_time_to_first_pixel (2way) (ms):          %.10f
Range_sampling_rate (computed, MHz):            %f
Total_range_band_width (MHz):                   %f
Weighting_range:                                %s

*******************************************************************
*_Start_leader_datapoints
*******************************************************************
t(s)            X(m)            Y(m)            Z(m)
NUMBER_OF_DATAPOINTS:   %d
'''
	sys.stdout.write(str0 % (d['product'],
	       d['dummy'],
	       d['dummy'],
	       d['dummy'],
	       d['checknumlines'],
	       d['producttype'],
	       d['sarprocessor'],
	       d['swath'],
	       d['pass'],
	       d['frequency'],
	       d['dummy'],
	       d['dummy'],
	       d['dummy'],
	       d['dummy'],
	       d['dummy'],
	       d['product'],
	       d['producttype'],
	       d['center_lat'],
	       d['center_lon'],
               d['heading'],
	       np.double(d['radar_wavelength']),
	       d['firstlinetime'],
	       d['lastlinetime'],
	       np.double(d['prf']),
	       np.double(d['abw']),
	       d['dummy'],
	       np.double(d['fd1']),
	       np.double(d['fdd1']),
	       np.double(d['fddd1']),
	       d['twt'],
	       d['rng_samp_rate'],
	       d['rbw'],
	       d['dummy'],
	       d['numstatevectors']) );

	# Dump the state vectors in the required format...
	# $AWK '/^time_of_first_state_vector/{t=$2};/^state_vector_interval/{dt=$2;c=0};/^state_vector_position/{ printf "%.6f\t%.3f\t%.3f\t%.3f\n", t+(c++)*dt, $2, $3, $4 }' $PARFILE
        for k in xrange(len(d['sv'])):
            sys.stdout.write(str("%f\t%f\t%f\t%f\n" %(d['sv'][k,0], d['sv'][k,1], d['sv'][k,2], d['sv'][k,3])))
	# Dump the closing section...
       
	sys.stdout.write('''
*******************************************************************
* End_leader_datapoints:_NORMAL
*******************************************************************
Datafile:    %s
Number_of_lines_original:                       %d
Number_of_pixels_original:                      %d
*******************************************************************
* End_readfiles:_NORMAL
*******************************************************************

	''' % (d['slcfile'],
	       d['calc_num_lines'],
	       int(d['num_rng_bins'])))

def bsq2bip(slcfile, width):
  #print('...Reading the data file...');
  if not os.access(slcfile+'.ci2', os.R_OK):
    data=adore.getdata(slcfile, width, 'ci2', interleave='bsq');  
    #dataR=(data.real/2**16).astype(int)+1j*(data.imag/2**16).astype(int);
    #print('...Writing doris compatible slc file');
    adore.writedata(slcfile+'.ci2', data, 'ci2');

if __name__=='__main__':
  main(sys.argv[1:]);

