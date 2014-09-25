# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 11:03:40 2010
@author: bosmanoglu

res2h5ich(resfiles, h5fname=None, products=['interfero','coherence','*.srph2ph'], width=None, formats=None, wl=0.0562356, ml=[1,1], crop='[0:,0:]')
res2dict(resfile)
isresfile(resfile,lines=30)
getdata(fname, width, dataFormat, length=0)
getProduct(rdict, process, filename=None, width=None, dataFormat=None)
getval(fileDict, key, lines=None, processName=None, regexp=None)
process2dict(fileDict, processName)
file2dict(filename)
mres2dicts(resfiles)
"""
import os, re
import numpy as np
import basic 
import string

class Object:
    """ADORE Object
    cmd("adore command", mobj=A.mobj, sobj=A.sobj, iobj=A.iobj, setobj=A.setobj)
    """
                
    def __init__(self, settingsFile=None):
        self.settingsFile=settingsFile
        if settingsFile is None:
            #Initialize barebones
            pass
        else:
            try:
                settings=parseSettings(self.settingsFile);
                self.settings=settings
                self.setobj=dict2obj(settings._sections, lambda x: string.strip(x, '"'));
            except:
                self.settings=None
                self.setobj=None                        
            try:
                self.ires=res2dict( settings.get('general', 'i_resfile') );
                self.iobj=dict2obj(self.ires);
            except:
                self.ires=None
                self.iobj=None
            try:
                self.mres=res2dict( settings.get('general', 'm_resfile') );
                self.mobj=dict2obj(self.mres);
            except:
                self.mres=None
                self.mobj=None
            try:
                self.sres=res2dict( settings.get('general', 's_resfile') );
                self.sobj=dict2obj(self.sres);
            except:
                self.sres=None
                self.sobj=None
        
        self.pn2rs=basic.rkdict({
          'm_readfiles'  :'readfiles',   
          's_readfiles'  :'readfiles',
          'coarseorb'    :'coarse_orbits',
          'demassist'    :'dem_assist',      
          'subtrrefpha'  :'subtr_refphase',  
          'dinsar'       :'dinsar'        ,  
          'm_porbits'    :'precise_orbits',  
          's_porbits'    :'precise_orbits',  
          'coarsecorr'   :'coarse_correl' ,  
          'coregpm'      :'comp_coregpm'  ,  
          'comprefdem'   :'comp_refdem'   ,  
          'slant2h'      :'slant2h'       ,  
          'm_crop'       :'crop'          ,  
          's_crop'       :'crop'          ,  
          'm_filtazi'    :'filt_azi'      ,  
          'resample'     :'resample'      , 
          'subtrrefdem'  :'subtr_refdem'  ,  
          'geocode'      :'geocoding'     , 
          'm_simamp'     :'sim_amplitude' , 
          's_filtazi'    :'filt_azi'      , 
          'filtrange'    :'filt_range'    , 
          'coherence'    :'coherence'     , 
          'm_timing'     :'master_timing' , 
          'fine'         :'fine_coreg'    , 
          'interfero'    :'interfero'     , 
          'filtphase'    :'filtphase'     , 
          'm_ovs'        :'oversample'    , 
          's_ovs'        :'oversample'    , 
          'reltiming'    :'timing_error'  , 
          'comprefpha'   :'comp_refphase' , 
          'unwrap'       :'unwrap'        , 
          'ci2'          :'complex_short' , 
          'cr4'          :'complex_real4' , 
          'i2'           :'short'         , 
          'r4'           :'real4'})          

    def addResults(self,process,d):
        """addResults(process, data_object)
          Add process results to the end of result file. 
          data_object is the subsection of mobj, sobj or iobj.
        """
        stars="*******************************************************************"
        if "m_" in process:
            filename=self.setobj.general.m_resfile.strip('"')
        elif "s_" in process:
            filename=self.setobj.general.s_resfile.strip('"')
        else:
            filename=self.setobj.general.i_resfile.strip('"')

        resname=self.pn2rs[process];
        f=open(filename, 'a');
        fwrite=lambda x: f.write(x+'\n');
        if resname == "master_timing":
            fwrite(stars)
            fwrite('*_Start_master_timing: ')
            fwrite(stars)
            fwrite('Correlation method                      :       %s' % d.Correlation_method)
            fwrite('Number of correlation windows used      :       %s' % d.Number_of_correlation_windows_used)
            fwrite('Estimated translation master w.r.t. synthetic amplitude (master-dem):')
            if d.Coarse_correlation_translation_lines >= 0:
                fwrite('  Positive offsetL: master image is to the bottom')
            else:
                fwrite('  Negative offsetL: master image is to the top')                
            if d.Coarse_correlation_translation_pixels >= 0:
                fwrite('  Positive offsetP: master image is to the right')
            else:
                fwrite('  Negative offsetP: master image is to the left')                
            fwrite('Coarse_correlation_translation_lines    :       %f' % d.Coarse_correlation_translation_lines)
            fwrite('Coarse_correlation_translation_pixels   :       %f' % d.Coarse_correlation_translation_pixels)
            fwrite('Master_azimuth_timing_error             :       %.9f sec.' % d.Master_azimuth_timing_error)
            fwrite('Master_range_timing_error               :       %e sec.' % d.Master_range_timing_error)
            fwrite(stars)
            fwrite('* End_master_timing:_NORMAL');
            fwrite(stars);
        elif resname=='coarse_correl':
            fwrite(stars);
            fwrite('*_Start_coarse_correl: ')
            fwrite(stars)
            fwrite('Estimated translation slave w.r.t. master:')
            fwrite('Coarse_correlation_translation_lines:   %d' %d.Coarse_correlation_translation_lines)
            fwrite('Coarse_correlation_translation_pixels:  %d' %d.Coarse_correlation_translation_pixels)
            fwrite('Number of correlation windows:          %s' %d.Number_of_correlation_windows)
            fwrite('')
            fwrite('#     center(l,p)   coherence   offsetL   offsetP')
            for k in xrange(d.results.shape[0]):
                fwrite('%d	%d	%d	%f	%d	%d' %(d.results[k,0], d.results[k,1], d.results[k,2], d.results[k,3], d.results[k,4], d.results[k,5]))
            fwrite('')
            fwrite(stars)
            fwrite('* End_coarse_correl:_NORMAL');                         
            fwrite(stars)
        fwrite('');
        f.close();
        basic.findAndReplace(filename, resname+':\t\t0', resname+':\t\t1')
        #basic.findAndReplace(filename, 'master_timing', process+':\t\t1')
#    def updateResults(self, process,d):
#        stars="*******************************************************************"
#        if "m_" in process:
#            filename=self.setobj.general.m_resfile.strip('"')
#        elif "s_" in process:
#            filename=self.setobj.general.s_resfile.strip('"')
#        else:
#            filename=self.setobj.general.i_resfile.strip('"')

#        resname=self.pn2rs[process];
#        if resname == "crop":
#            basic.findAndReplace(filename, resname+':\t\t0', resname+':\t\t1')
    def cmd(self, c, mobj=None, sobj=None, iobj=None, setobj=None):
        from subprocess import call
        call(['adore', '-u', self.settingsFile, c]) 
        self.__init__(self.settingsFile)    
    
    def modifyResults(self, process, parameter, value):
        from subprocess import call
        if "m_" in process:
            filename=self.setobj.general.m_resfile.strip('"')
        elif "s_" in process:
            filename=self.setobj.general.s_resfile.strip('"')
        else:
            filename=self.setobj.general.i_resfile.strip('"')

        resname=self.pn2rs[process];
        call(['modifyRes.sh',filename, resname, parameter, value]) 

    def modifyResultRe(self, process, searchPattern, replacePattern):
        import fileinput
        import re
        if "m_" in process:
            filename=self.setobj.general.m_resfile.strip('"')
        elif "s_" in process:
            filename=self.setobj.general.s_resfile.strip('"')
        else:
            filename=self.setobj.general.i_resfile.strip('"')

        resname=self.pn2rs[process];
        
        pflag=False #process Flag
        for line in fileinput.input([filename], inplace=1):
            if 'Start_'+resname in line:
                pflag=True
            elif 'End_'+resname in line:
                pflag=False
            if pflag==True:
                line=re.sub(searchPattern, replacePattern, line);
            sys.stdout.write(line)

    def modifyResult(self, process, parameter, value):
        import fileinput
        if "m_" in process:
            filename=self.setobj.general.m_resfile.strip('"')
        elif "s_" in process:
            filename=self.setobj.general.s_resfile.strip('"')
        else:
            filename=self.setobj.general.i_resfile.strip('"')

        resname=self.pn2rs[process];
        
        pflag=False #process Flag
        for line in fileinput.input([filename], inplace=1):
            if 'Start_'+resname in line:
                pflag=True
            elif 'End_'+resname in line:
                pflag=False
            if (pflag==True) & (parameter in line):
                line=line.replace(line.split(':')[-1], value); #replace the last value after : with the new value.
            sys.stdout.write(line)
                        
#def dict2obj(d):
#    class DictObj(object):
#        def __init__(self,d):
#            self.d=d
#        def __getattr__(self, m):
#            return self.d.get(m,None)     
#    do = DictObj(d)
#    return do

def dict2obj(d, fun=None):
    """dict2obj(d, fun=None)
    dict2obj(d, fun=string.strip())
    """
    #Modified from
    #Ygor Lemos: parand.com/say/index.php/2008/10/13/access-python-dictionary-keys-as-properties/
    class DictObj:
        def __init__(self, **entries):
            for e in entries:
                #No space and dot for attribute name
                et="_".join(e.split())
                et=et.replace('.','')
                if isinstance(d[e], dict):
                    self.__dict__[et]=dict2obj(d[e])
                else:
                    if fun is not None:
                      self.__dict__[et]=fun(d[e])
                    else:
                      self.__dict__[et]=d[e]                
    return DictObj(**d)
  
def res2dict(resfile):
    '''dict=res2dict(resfile)
    Converts a doris resultfile into a python dict.    
    '''

    #Change this code to also return a dictionary of line numbers for each part of the file.__class__
    #Something like this might help:
#    while str(cntr) in res:
#      if res[str(cntr)].find('End_')>-1:
#        res[str(cntr)]
#      cntr=cntr+1  
    res=file2dict(resfile);    
    out={}
    out['resfile']=os.path.abspath(resfile);
    #get file type (master, slave, interferogram)
    out['restype']=res['2'].split(' ',2)[1] #Returns MASTER, SLAVE or INTERFEROGRAM    
    #read process flags
    out['process_control']={}
    cntr=3 # start from line 3. 
    flag=False;
    while str(cntr) in res:
        if res[str(cntr)].find('End_process_control')>-1: #if found
            break
        #split left and right 
        if flag==False:
            if res[str(cntr)].find('Start_process_control')>-1:
                flag=True
                cntr=cntr+1;
                continue
            else:
                cntr=cntr+1;
                continue                   
        [key,val]=res[str(cntr)].split(':',2)                
        out['process_control'][key.strip()]=int(val.strip())
        cntr=cntr+1;
    
    #loop over process control and read each output
    for key in out['process_control'].keys():
        if key=='NOT_USED':
            continue
        out[key]=process2dict(res,key);
    return out

def drs2dict(resfile):
    '''dict=drs2dict(resfile)
    Converts a doris input file into a python dict.    
    '''

    res=file2dict(resfile);    
    out={}
    out['drsfile']=os.path.abspath(resfile);
    #read process flags
    out['process']=[]
    out['process'].append('general')
    cntr=1 # start from line 3. 
    while str(cntr) in res:
        if res[str(cntr)].find('stop')>-1: #if found
            break
        #split left and right 
        if res[str(cntr)].find('process')==0:
            out['process'].append(res[str(cntr)].split()[1] )
            cntr=cntr+1;
            continue
        else:
            cntr=cntr+1;
            continue                   
        cntr=cntr+1;
    
    #loop over process control and read each output
    for key in out['process']:
        out[key]=process_input2dict(res,key);
    return out


def mres2dicts(resfiles):
    ''' [dct0, dct1...]=adore.mres2dicts([res0, res1,...]);
    '''
    if len(resfiles)==1:
      return [res2dict(resfiles)];
    else:
      out=[]
      for file in resfiles:
          out.append(res2dict(file))
      return out

def file2dict(filename):
    '''dict=file2dict(filename)
    Read file contents (text) to a dictionary where keys are line numbers.
    '''
    if os.path.isfile(filename):
        FH=open(filename, 'r'); #FD: file handle
        line=FH.readline();
        out={}
        cntr=1 #counter
        while line: 
            key=str(cntr)
            out[key]=line
            cntr=cntr + 1
            line=FH.readline()
        FH.close()
    else:
        print "Can not open file: ", filename;
        return {} #an empty dict
    return out

def process_input2dict(fileDict, processName):
    '''dict=process2dict(filedict, processName)
    '''
    if processName == 'general':
        reDict = {'screen': None,
                  'beep': None,
                  'batch': None,
                  'overwrite': None, 
                  'preview': None,
                  'listinput': None,
                  'memory': None,
                  'logfile': None,
                  'm_resfile': None,
                  's_resfile': None,
                  'i_resfile': None,
                  'orb_interp': None,
                  'orb_prm': None,
                  'dumpbaseline': None,
                  'height': None,
                  'tiepoint': None,
                  'm_rg_t_error': None, 
                  'm_az_t_error': None,
                  's_rg_t_error': None,
                  's_az_t_error': None
                  }
    else:
        return {}

    out={}    
    for key in reDict:
        if reDict[key] is None:
            reDict[key]=key + '[\s]+(.*)//.*\n'
        val=getval(fileDict,key, None, None, reDict[key])
        if val is None:
            continue
        else:
            out[key]=val
    return out
    
def process2dict(fileDict, processName):
    '''dict=process2dict(filedict, processName)
    '''
    if processName == 'readfiles':
        reDict = {'Volume file': None,
                  'Volume_ID': None,
                  'Xtrack_f_DC_constant': None,
                  'Scene_centre_latitude': None,
                  'Scene_centre_longitude': None,
                  'Radar_wavelength': "Radar_wavelength.*:[\s]+(.*)",
                  'First_pixel_azimuth_time': "First_pixel_azimuth_time.*:[\s]+(.*)",
                  'Pulse_Repetition_Frequency': "Pulse_Repetition_Frequency.*:[\s]+(.*)",
                  'Total_azimuth_band_width': "Total_azimuth_band_width.*:[\s]+(.*)",
                  'Xtrack_f_DC_constant': "Xtrack_f_DC_constant.*:[\s]+(.*)",
                  'Xtrack_f_DC_linear': "Xtrack_f_DC_linear.*:[\s]+(.*)",
                  'Xtrack_f_DC_quadratic': "Xtrack_f_DC_quadratic.*:[\s]+(.*)",
                  'Range_time_to_first_pixel': "Range_time_to_first_pixel.*:[\s]+(.*)",
                  'Range_sampling_rate': "Range_sampling_rate.*:[\s]+(.*)",
                  'Total_range_band_width': "Total_range_band_width.*:[\s]+(.*)",
                  'NUMBER_OF_DATAPOINTS': "NUMBER_OF_DATAPOINTS:[\s]+(.*)",
                  }
    elif processName == 'crop':
        reDict = {'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,                 
                  }
    elif processName == 'sim_amplitude':
        reDict = {'DEM source file': None,
                  'Min. of input DEM': None,
                  'Max. of input DEM': None,
                  'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None, 
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,                 
                  'Number of lines': None,
                  'Number of pixels': None,                            
                  }

    elif processName == 'master_timing':
        reDict = {'Correlation method': None,
                  'Number of correlation windows used': None,
                  'Coarse_correlation_translation_lines': None,
                  'Coarse_correlation_translation_pixels': None,
                  'Master_azimuth_timing_error': None,
                  'Master_range_timing_error': None,
                  }
    elif processName == 'filt_azi':
        reDict = {'Input_file': None,
                  'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,
                  }
    elif processName == 'filt_range':
        reDict = {'Method_rangefilt': None,
                  'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,
                  }
    elif processName == 'coarse_orbits':
        reDict = {'Btemp': "\s+Btemp:\s+\[days\]:(.*)//.*",
                  'Bperp': "\s+Bperp.*:(.*)//.*",
                  'Bpar': "\s+Bpar.*:(.*)//.*",
                  'Bh': "\s+Bh.*:(.*)//.*",
                  'Bv': "\s+Bv.*:(.*)//.*",
                  'B': "\s+B\s+\[m\]:[\s]+(.*)//.*",
                  'alpha': "\s+alpha.*:(.*)//.*",
                  'theta': "\s+theta.*:(.*)//.*",
                  'inc_angle': "\s+inc_angle.*:(.*)//.*",
                  'orbitconv': "\s+orbitconv.*:(.*)//.*",
                  'Height_amb': "\s+Height_amb.*:(.*)//.*",
                  'Coarse_orbits_translation_lines': None,  
                  'Coarse_orbits_translation_pixels': None,
                  }
    elif processName == 'coarse_correl':
        reDict = {'Coarse_correlation_translation_lines': None,
                  'Coarse_correlation_translation_pixels': None,
                  'Number of correlation windows': None,
                  }                  
    elif processName == 'fine_coreg':
        reDict = {'Initial offsets': None,
                  'Window_size_L_for_correlation': None,
                  'Window_size_P_for_correlation': None,
                  'Max. offset that can be estimated': None,
                  'Peak search ovs window': None,
                  'Oversampling factor': None,
                  'Number_of_correlation_windows': None,                  
                  }
    elif processName == 'timing_error':
        reDict = {'Orbit_azimuth_offset': None,
                  'Orbit_range_offset': None,
                  'Estimated_azimuth_offset': None,
                  'Estimated_range_offset': None,
                  'Estimated_azimuth_timing_error_lines': None,
                  'Estimated_range_timing_error_pixels': None,
                  'Estimated_azimuth_timing_error_sec': None,
                  'Estimated_range_timing_error_sec': None,
                  }                  
    elif processName == 'dem_assist':
        reDict = {'DEM source file': None,
                  'Min. of input DEM': None,
                  'Max. of input DEM': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,
                  'Number of lines': None,
                  'Number of pixels': None,
                  'Deltaline_slave00_dem': None,
                  'Deltapixel_slave00_dem': None,
                  'Deltaline_slave0N_dem': None,
                  'Deltapixel_slave0N_dem': None,
                  'Deltaline_slaveN0_dem': None,
                  'Deltapixel_slaveN0_dem': None,
                  'Deltaline_slaveNN_dem': None,
                  'Deltapixel_slaveNN_dem': None,
                  }                  
    elif processName == 'comp_coregpm':
        reDict = {'Degree_cpm': None,
                  'Deltaline_slave00_poly': None,
                  'Deltapixel_slave00_poly': None,
                  'Deltaline_slave0N_poly': None,
                  'Deltapixel_slave0N_poly': None,
                  'Deltaline_slaveN0_poly': None,
                  'Deltapixel_slaveN0_poly': None,
                  'Deltaline_slaveNN_poly': None,
                  'Deltapixel_slaveNN_poly': None,
                  }
    elif processName == 'interfero':
        reDict = {'Data_output_file': "Data_output_file:[\s]+(.*)",
                  'Data_output_format': "Data_output_format:[\s]+(.*)",
                  'Data_output_file_real_interferogram': None,
                  'Data_output_format_real_interferogram': None,
                  'Flatearth correction subtracted': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Number of lines': None,
                  'Number of pixels': None,                     
                  }                  
    elif processName == 'comp_refphase':
        reDict = {'Degree_flat': None,
                  'Degree_h2ph': None,
                  }
    elif processName == 'subtr_refphase':
        reDict = {'Method': None,
                  'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Number of lines': None,
                  'Number of pixels': None,   
                  }
    elif processName == 'comp_refdem':
        reDict = {'Include_flatearth': None,
                  'DEM source file': None,
                  'Min. of input DEM': None,
                  'Max. of input DEM': None,
                  'Data_output_file': None,
                  'Data_output_format': None,                  
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Number of lines': None,
                  'Number of pixels': None,
                  }
    elif processName == 'subtr_refdem':
        reDict = {'Method': None,
                  'Additional_azimuth_shift': None,
                  'Additional_range_shift': None,
                  'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Number of lines': None,
                  'Number of pixels': None,   
                  }                  
    elif processName == 'coherence':
        reDict = {'Method': None,
                  'Data_output_file': "Data_output_file:[\s]+(.*)",
                  'Data_output_format': "Data_output_format:[\s]+(.*)",
                  'Data_output_file_complex_coherence': None,
                  'Data_output_format_complex_coherence': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Number of lines': None,
                  'Number of pixels': None,   
                  }
    elif processName == 'filtphase':
        reDict = {'Method_phasefilt': "Method_phasefilt:[\s]+(.*)",
                  '1D Smoothing kernel': "1D Smoothing kernel for |spectrum|:[\s]+(.*)" ,
                  'Input_file': None,
                  'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Number of lines': None,
                  'Number of pixels': None,   
                  }
    elif processName == 'geocoding':
        reDict = {'Data_output_file_hei': "Data_output_file_hei.*:[\s]+(.*)",
                  'Data_output_file_phi': "Data_output_file_phi:[\s]+(.*)",
                  'Data_output_file_lamda': "Data_output_file_lamda:[\s]+(.*)",
                  'Data_output_format': "Data_output_format:[\s]+(.*)",
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  }
    elif processName == 'slant2h':
        reDict = {'Method': None,
                  'Data_output_file': "Data_output_file:[\s]+(.*)",
                  'Data_output_format': "Data_output_format:[\s]+(.*)",
                  'Data_output_file_phi': None,
                  'Data_output_file_lam': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Ellipsoid': "Ellipsoid.*:[\s]+(.*)",
                  }                        
    elif processName == 'unwrap':
        reDict = {'Data_output_file': None,
                  'Data_output_format': None,
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  'Number of lines': None,
                  'Number of pixels': None,   
                  'Program used for unwrapping': None,
                  }                  
    elif processName == 'geocoding':
        reDict = {'Data_output_file_hei': "Data_output_file (slant2h):[\s]+(.*)",
                  'Data_output_file_phi': None,
                  'Data_output_file_lamda': None,
                  'Data_output_format': "Data_output_format:[\s]+(.*)",
                  'First_line': None,
                  'Last_line': None,
                  'First_pixel': None,
                  'Last_pixel': None,   
                  'Multilookfactor_azimuth_direction': None,
                  'Multilookfactor_range_direction': None,
                  }                        
    
#    elif processName == '':
#        reDict = {'': None,
#                  '': None,
#                  '': None,
#                  }

    else:
        return {}

    lStart,lEnd=getProcessLines(fileDict, processName)        
    lines=[]
    for k in np.r_[lStart:lEnd]:
        lines.append(str(k))
    
    out={}    
    for key in reDict:
        val=getval(fileDict,key, lines,processName, reDict[key])
        if val is None:
            continue
        else:
            out[key]=val

    #Start process specific extraction... 
    if processName=="coarse_correl" and out['Number of correlation windows']:
        out['results']=csv2Array(fileDict, lStart+8, int(out['Number of correlation windows'].split("of")[0]), 6, dtype=np.float)
    elif processName=="fine_coreg":
        try:
            out['results']=csv2Array(fileDict, lStart+10, int(out['Number_of_correlation_windows']), 6, dtype=np.float)
        except:
            pass
    elif processName=="comp_coregpm" and out['Degree_cpm']:       
        #Below equation is from doris/src/utilities.hh Line:100, 
        numCoef=int(np.fix(0.5*((out['Degree_cpm']+1)**2+out['Degree_cpm']+1)))#[1,3,6,10]#2*(int(out['Degree_cpm'])+1)
        out['Estimated_coefficientsL']=csv2Array(fileDict,lStart+4, numCoef, 3, dtype=np.float) # numCoef[int(out['Degree_cpm'])]
        out['Estimated_coefficientsP']=csv2Array(fileDict,lStart+6+numCoef  , numCoef, 3, dtype=np.float)        
    elif processName=="comp_refphase" and out['Degree_flat']:
        numCoef=int(np.fix(0.5*((out['Degree_flat']+1)**2+out['Degree_flat']+1)))
        out['Estimated_coefficients_flatearth']=csv2Array(fileDict,lStart+4          , numCoef, 3, dtype=np.float)
        out['Estimated_coefficients_h2ph']     =csv2Array(fileDict,lStart+8+numCoef  , numCoef, 3, dtype=np.float)        
    elif processName=="readfiles" and out['NUMBER_OF_DATAPOINTS']:
        lStart,lEnd=getProcessLines(fileDict, 'leader_datapoints')
        out['leader_datapoints']=csv2Array(fileDict, lStart+4, out['NUMBER_OF_DATAPOINTS'], 4, dtype=np.float)
    
    return out
    
def getval(fileDict, key, lines=None, processName=None, regexp=None):
    '''value=getval(fileDict, key, lines=None, processName=None)
    '''
    #check if dict. If not assume path.
    if not isinstance(fileDict, dict):
        fileDict=file2dict(fileDict);
    #Now check lines or processName
    if (lines is None) and (processName is None):
        lines=[];
        for k in fileDict.keys():
            if fileDict[k].find(key)>-1:
                lines.append(k)
    if lines is None: #this means processName is given but lines is empty.
        lstart,lend=getProcessLines(fileDict, processName)        
        lines=[]
        for k in np.r_[lstart:lend]:
            lines.append(str(k))
        
    out=[];
    if regexp is None:
        regexp=key + ".*:[\s]+(.*)"
    for l in lines:
        if not isinstance(l, str):
            lstr=str(l)
        else:
            lstr=l        
        m=re.match(r"" +regexp + "",fileDict[lstr])
        if m is None:
            continue
        else:
            try:
                out.append(int(m.group(1)))
            except:
                try:
                    out.append(float(m.group(1)))
                except:
                    out.append(m.group(1))

    if len(out)==1:
        out=out[0]; #if singleton return value not a list.
    return out

def getdata(fname, width, dataFormat, length=0, byteswap=False, skipbytes=0, interleave='bip'):  
    datatype, complexFlag=dataFormat2dataType(dataFormat);        
    if complexFlag==True:
        width=2*width;

    if length==0:
        filesize=os.path.getsize(fname)
        length=float(filesize-skipbytes)/width/np.dtype(datatype).itemsize
        if not basic.isint(length):
            print("Error with file width, will continue but results might be bad.")
            print('Width(*2 if complex): %d, Length: %.2f, FileSize: %d' % (width,length,filesize) )
        length=int(length);

    f=open(fname, "rb")
    if skipbytes > 0:
        f.seek(skipbytes, os.SEEK_SET)
    
    if complexFlag:
        data=np.fromfile(f, datatype ,width*length).reshape(length, width)
        #data=np.vectorize(complex)(data[:,0:-1:2],data[:,1::2])
        if byteswap:
            data.byteswap(True);
        if interleave=='bip':
          data=data[:,0:-1:2]+1j*data[:,1::2]
          #data=np.zeros((length,width/2),np.complex);
          #data+=dataP;
        elif interleave=='bil':
          data=data[0:-1:2,:]+1j*data[1::2,:]
	elif interleave=='bsq':
	  data=data[:,0:width/2]+1j*data[:,width/2:];
	  #data=data[:,0:6144]+1j*data[:,6144:];
    else:        
        data=np.fromfile(f, datatype ,width*length).reshape(length, width)
        if byteswap:
            data.byteswap(True);
    f.close()
    return data

def getProcessLines(fileDict, processName):
    """
    lstart,lend=getProcessLines(fileDict, processName);
    Returns -1 if can not find start or end of process.
    """
    lstart=-1;lend=-1
    for k in fileDict.keys():
        if fileDict[str(k)].find('Start_'+processName)>-1:
            lstart=int(k);
        if fileDict[str(k)].find('End_'+processName)>-1:
            lend=int(k);
        if lstart>-1 and lend>-1:
            break
    return (lstart, lend)

def csv2Array(fileDict, lStart, rows, cols, dtype=np.float):
    '''
    csv2Array(fileDict, lStart, rows, cols, dtype=np.float):
    '''
    out=np.empty((rows,cols), dtype);
    for r in xrange(rows):
        out[r,:]=np.fromstring(fileDict[str(lStart+r)], dtype, cols, ' ')
    return out

def dataFormat2dataType(dataFormat):
    complexFlag=False;
    #### Handle the long format specifier: i.e. complex_real4
    if "real4" in dataFormat:
        datatype="f4"
    elif "short" in dataFormat:
        datatype="i2"
    else:
        datatype=dataFormat

    if "complex" in dataFormat:
        complexFlag=True;
    ### Handle the short format specifier: i.e. cr4    
    if dataFormat=="cr2":
        datatype=np.half        
        complexFlag=True;
    elif dataFormat=="r2":
        datatype=np.half
    elif dataFormat=="cr4":
        datatype="f4"        
        complexFlag=True;
    elif dataFormat=="r4":
        datatype="f4"
    elif dataFormat=="cr8":
        datatype="f8"        
        complexFlag=True;
    elif dataFormat=="r8":
        datatype="f8"
    elif dataFormat=="ci2":
        datatype="i2"
        complexFlag=True;
    elif  dataFormat=="i2":
        datatype="i2"
    elif dataFormat=="ci4":
        datatype="i4"
        complexFlag=True;
    elif dataFormat=="cc1":
        datatype="i1"
        complexFlag=True;        
    elif dataFormat=="c1":
        datatype="i1"
    elif dataFormat=="cu1":
        datatype="u1"
        complexFlag=True;                
    elif dataFormat=="u1":
        datatype="u1"
    elif  dataFormat=="u2":
        datatype="u2"
    elif  dataFormat=="cu2":
        datatype="cu2"
    #else: dtype is already set to dataFormat
    return (datatype, complexFlag);    
    
def isresfile(resfile,lines=30):  
    '''
       isresfile('/path/to/result/file.res')
       Returns true if given file is a DORIS result file.
    '''
    if os.path.isfile(resfile):
        FH=open(resfile, 'r');
        for l in xrange(lines):
            line=FH.readline();
            if 'Start_process_control' in line:
                return True
        return False
    else:
        return False    

def writedata(fname, data, dataFormat):
    datatype,complexFlag=dataFormat2dataType(dataFormat);
    if complexFlag:
        bipData=np.empty([data.shape[0], data.shape[1]*2]);
        bipData[:,0::2]=data.real;
        bipData[:,1::2]=data.imag;
        bipData.astype(np.dtype(datatype)).tofile(fname) 
    else:
        data.astype(np.dtype(datatype)).tofile(fname) 

def getProduct(rdict, process=None, filename=None, width=None, dataFormat=None):
    """getProduct(rdict, process=None, filename=None, width=None, dataFormat=None)
    ex:
    A=getProduct(iobj.geocoding)
    A=getProduct(ires, 'geocoding')
    """
    #check if idict or iobj
    if (process is None) & (isinstance(rdict, dict)):
        print "Please provide either result object or resdict and process name."
        return -1
    if process==None:
        if filename is None:
            filename=rdict.Data_output_file
        if width is None:
            if hasattr(rdict,'Number of pixels'):
                width=int(rdict.Number_of_pixels)
            elif hasattr(rdict,'Multilookfactor_range_direction'):
                width=int( (int(rdict.Last_pixel)-int(rdict.First_pixel)+1)/rdict.Multilookfactor_range_direction )
            else:
                width=int( (int(rdict.Last_pixel)-int(rdict.First_pixel)+1) )
        if dataFormat is None:
            dataFormat=rdict.Data_output_format       
    else:
        if filename is None:
            filename=rdict[process]['Data_output_file']
        if width is None:
            if rdict[process].has_key('Number of pixels'):
                width=int(rdict[process]['Number of pixels'])
	    elif rdict[process].has_key('Multilookfactor_range_direction'):
                width=int( (int(rdict[process]['Last_pixel'])-int(rdict[process]['First_pixel'])+1) /rdict[process]['Multilookfactor_range_direction'] )
            else:
		width=int(rdict[process]['Last_pixel'])-int(rdict[process]['First_pixel'])+1
        if dataFormat is None:
            dataFormat=rdict[process]['Data_output_format']        
    return getdata(filename, width, dataFormat);

def parseSettings(filename):
    """
    s=parseSettings('settings.set')
    """
    import ConfigParser
    class AdoreConfigParser(ConfigParser.RawConfigParser):
        def get(self, section, option):
            val = ConfigParser.RawConfigParser.get(self, section, option)
            return val.lstrip('"').rstrip('"')

    s=AdoreConfigParser();
    s.read(filename);
    return s

def polyval(x,y,coeff):
    """
    polyval(x,y,coeff)
    FOR compatibility with DORIS:
    -2<x<2
    -2<y<2
    """ 
    out=np.zeros(x.shape);   
    for k in np.arange(0,coeff.shape[1]):
        out += coeff[k,0]*np.power(x,coeff[k,1])*np.power(y, coeff[k,2]);
    return out

def h2ph(rdict, data, wl=0.0562356, h2phProcess='subtr_refphase', fileName=None, width=None, dataFormat='r4', bistatic=False):
    """h2ph(rdict, data, wl=0.0562356, h2ph_process='subtr_refphase', fileName=None, width=None, dataFormat=None, bistatic=False)
    Multiply the data with the height-to-phase(h2ph) conversion factor.
    """
    #data=getProduct(rdict, process, filename=fileName, width=width, dataFormat=dataFormat);
    if fileName is None:
        fileName=rdict[h2phProcess]['Data_output_file']+'h2ph'
    h2ph=getProduct(rdict, h2phProcess, filename=fileName, width=width, dataFormat=dataFormat);
    if bistatic:
        multiplier=-2*np.pi/wl;
    else:
        multiplier=-4*np.pi/wl;
    return data*h2ph*multiplier;

def ph2h(rdict, data, wl=0.0562356, h2phProcess='subtr_refphase', fileName=None, width=None, dataFormat='r4', bistatic=False):
    """h2ph(rdict, data, wl=0.0562356, h2ph_process='subtr_refphase', fileName=None, width=None, dataFormat=None, bistatic=False)
    Divide the data with the height-to-phase(h2ph) conversion factor.
    Convert phase to height.
    """
    #data=getProduct(rdict, process, filename=fileName, width=width, dataFormat=dataFormat);
    if fileName is None:
        fileName=rdict[h2phProcess]['Data_output_file']+'h2ph'
    h2ph=getProduct(rdict, h2phProcess, filename=fileName, width=width, dataFormat=dataFormat);
    if bistatic:
        h2ph=h2ph*-2*np.pi/wl;
    else:
        h2ph=h2ph*-4*np.pi/wl;
    return data/h2ph;
    
def latlon2lp(iobj, lat, lon):
    """latlon2lp(iobj, lat, lon)
    """
    LAT=getProduct(iobj.geocoding, filename=iobj.geocoding.Data_output_file_phi)
    LON=getProduct(iobj.geocoding, filename=iobj.geocoding.Data_output_file_lamda)
    #calculate shortest distance
    LAT=abs(LAT-lat)
    LON=abs(LON-lon)
    d=LAT+LON
    return basic.ind2sub(LAT.shape,d.argmin())


