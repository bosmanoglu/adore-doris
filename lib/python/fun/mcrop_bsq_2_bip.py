filesize=os.path.getsize(mobj.crop.Data_output_file);
width=mobj.crop.Last_pixel-mobj.crop.First_pixel+1;
datatype, complexFlag=adore.dataFormat2dataType('ci4');
length=float(filesize)/width/np.dtype(datatype).itemsize/2; 
fileparts=fix(linspace(0, length, 10)).astype(int);
 
#data=adore.getdata(mobj.crop.Data_output_file,(mobj.crop.Last_pixel-mobj.crop.First_pixel+1), 'cr2', (mobj.crop.Last_line-mobj.crop.First_line+1));
#adore.writedata(mobj.crop.Data_output_file+'.cr4', data, 'cr4')
data=adore.getdata(setobj.m_crop_in, width, 'ci4', interleave='bsq');
adore.writedata(mobj.crop.Data_output_file, data, 'ci2');
#A.modifyResults('m_crop', 'Data_output_file', mobj.crop.Data_output_file);
#A.modifyResults('m_crop', 'Data_output_format', 'complex_real4')
