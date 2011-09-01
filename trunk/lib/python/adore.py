# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 11:03:40 2010

@author: bosmanoglu
"""
import os, re
import numpy as np
import tables
import basic
import insar
import path

def res2h5(resfiles, h5fname=None):
    ''' res2h5f(resfiles, filename=None )
    resfiles: List of strings for paths to interferogram result file.
    h5fname: Name of the output file.
    '''
    if h5fname==None:
        h5fname=resfiles[0].split(os.sep)[-2]+".h5"
    h5f = tables.openFile(h5fname, mode = "w", title = "ADORE Results")
    group = h5f.createGroup("/", 'insar', 'InSAR Results')
    
    for resfile in resfiles:
        #InCoh=insar.siminterf(dem,b,1,waterHeight)
        dct=res2dict(resfile)
        cint=getdata(dct['subtr_refphase']['Data_output_file'],dct['subtr_refphase']['Number of pixels'],dct['subtr_refphase']['Data_output_format'])
        coh=getdata(dct['coherence']['Data_output_file'],dct['coherence']['Number of pixels'],dct['coherence']['Data_output_format'])
        h2ph=getdata(dct['subtr_refphase']['Data_output_file']+"h2ph",dct['subtr_refphase']['Number of pixels'],"real4")
        stdpha=insar.coh2stdpha(coh,20,100);
        fd=path.fisherDistance2(cint,stdpha)
        b=np.array([dct['coarse_orbits']['Bperp']]); #array of 1x1
        if not group.__contains__('bperp'):
            bperpA=h5f.createEArray(group, 'bperp',  tables.Float64Atom(shape=b.shape), (0,), "Perpendicular Baseline", expectedrows=len(resfiles))
            cintA =h5f.createEArray(group, 'cint',   tables.ComplexAtom(itemsize=16,shape=cint.shape), (0,), "Complex Interferogram", expectedrows=len(resfiles))
            cohA  =h5f.createEArray(group, 'coh',    tables.Float64Atom(shape=coh.shape), (0,), "Coherence", expectedrows=len(resfiles))
            h2phA =h5f.createEArray(group, 'h2ph',   tables.Float64Atom(shape=coh.shape), (0,), "Height to Phase", expectedrows=len(resfiles))
            stdphaA=h5f.createEArray(group,'stdpha', tables.Float64Atom(shape=stdpha.shape), (0,), "Phase Standard Deviation", expectedrows=len(resfiles))
            fdA   =h5f.createEArray(group, 'fd',     tables.Float64Atom(shape=fd.shape), (0,), "Fishers Distance", expectedrows=len(resfiles))
        bperpA.append(b);
        cintA.append(cint);
        cohA.append(coh);
        h2phA.append(h2ph);
        stdphaA.append(stdpha);
        fdA.append(fd);
    h5f.close()
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
        

#    elif processName == '':
#        reDict = {'': None,
#                  '': None,
#                  '': None,
#                  }

    else:
        return {}
    
    out={}
    for key in reDict:
        val=getval(fileDict,key, None,processName, reDict[key])
        if val is None:
            continue
        else:
            out[key]=val
        
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
        lines=[];lstart=-1;lend=-1
        for k in fileDict.keys():
            if fileDict[str(k)].find('Start_'+processName)>-1:
                lstart=int(k);
            if fileDict[str(k)].find('End_'+processName)>-1:
                lend=int(k);
            if lstart>-1 and lend>-1:
                break
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

def getdata(fname, width, dataFormat, length=0):  
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
    elif dataFormat=="ci2":
        datatype="i2"
        complexFlag=True;
    elif  dataFormat=="i2":
        datatype="i2"
    #else: dtype is already set to dataFormat
        
    if complexFlag==True:
        width=2*width;

    if length==0:
        filesize=os.path.getsize(fname)
        length=float(filesize)/width/np.dtype(datatype).itemsize
        if not basic.isint(length):
            print("Error with file width, will continue but results might be bad.")
            print("Width(*2 if complex): %f, Length: %f, FileSize: %d" ,width,length,filesize)
        length=int(length);

    if complexFlag:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
        data=data[:,0:-1:2]+1j*data[:,1::2]
    else:
        data=np.fromfile(fname, datatype ,width*length).reshape(length, width)
    return data
    
    