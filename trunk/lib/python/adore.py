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
    
def process2dict(fileDict, processName):
    '''dict=process2dict(filedict, processName)
    '''
    if processName == 'readfiles':
        reDict = {'Volume file': None,
                  'Volume_ID': None,
                  'Xtrack_f_DC_constant': None,
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
    if processName=="coarse_correl":
        out['results']=csv2Array(fileDict, lStart+8, int(out['Number of correlation windows'].split("of")[0]), 6, dtype=np.float)
    if processName=="fine_coreg":
        try:
            out['results']=csv2Array(fileDict, lStart+10, int(out['Number_of_correlation_windows']), 6, dtype=np.float)
        except:
            pass
    if processName=="comp_coregpm":
        numCoef=[1,3,6,10]#2*(int(out['Degree_cpm'])+1)
        out['Estimated_coefficientsL']=csv2Array(fileDict,lStart+4, numCoef[int(out['Degree_cpm'])], 3, dtype=np.float)
        out['Estimated_coefficientsP']=csv2Array(fileDict,lStart+6+numCoef[int(out['Degree_cpm'])], numCoef[int(out['Degree_cpm'])], 3, dtype=np.float)        
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

def getdata(fname, width, dataFormat, length=0, byteswap=False):  
    datatype, complexFlag=dataFormat2dataType(dataFormat);        
    if complexFlag==True:
        width=2*width;

    if length==0:
        filesize=os.path.getsize(fname)
        length=float(filesize)/width/np.dtype(datatype).itemsize
        if not basic.isint(length):
            print("Error with file width, will continue but results might be bad.")
            print('Width(*2 if complex): %d, Length: %.2f, FileSize: %d' % (width,length,filesize) )
        length=int(length);

    if complexFlag:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
        #data=np.vectorize(complex)(data[:,0:-1:2],data[:,1::2])
        if byteswap:
            data.byteswap(True);
        data=data[:,0:-1:2]+1j*data[:,1::2]
        #data=np.zeros((length,width/2),np.complex);
        #data+=dataP;
    else:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
        if byteswap:
            data.byteswap(True);
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
    if dataFormat=="cr4":
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

def getProduct(rdict, process, filename=None, width=None, dataFormat=None):
    """getProduct(rdict, process, filename=None, width=None, dataFormat=None)
    """
    if filename is None:
        filename=rdict[process]['Data_output_file']
    if width is None:
        if rdict[process].has_key('Number of pixels'):
            width=int(rdict[process]['Number of pixels'])
        else:
            width=int(rdict[process]['Last_pixel'])-int(rdict[process]['First_pixel'])+1
    if dataFormat is None:
        dataFormat=rdict[process]['Data_output_format']        
    return getdata(filename, width, dataFormat);
       