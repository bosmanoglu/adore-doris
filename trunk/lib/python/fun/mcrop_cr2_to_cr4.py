filesize=os.path.getsize(mobj.crop.Data_output_file);
width=mobj.crop.Last_pixel-mobj.crop.First_pixel+1;
datatype, complexFlag=adore.dataFormat2dataType('cr2');
length=float(filesize)/width/np.dtype(datatype).itemsize/2; 
fileparts=fix(linspace(0, length, 10)).astype(int);
  
#data=adore.getdata(mobj.crop.Data_output_file,(mobj.crop.Last_pixel-mobj.crop.First_pixel+1), 'cr2', (mobj.crop.Last_line-mobj.crop.First_line+1));
#adore.writedata(mobj.crop.Data_output_file+'.cr4', data, 'cr4')
fout=open(mobj.crop.Data_output_file+'.cr4', 'wb');
for l in xrange(len(fileparts)-1):
  data=adore.getdata(mobj.crop.Data_output_file,(mobj.crop.Last_pixel-mobj.crop.First_pixel+1), 'cr2', fileparts[l+1]-fileparts[l], skipbytes=(fileparts[l]*width*np.dtype(datatype).itemsize*2));
  bipData=np.empty([fileparts[l+1]-fileparts[l], data.shape[1]*2]);
  #bipData[:,0::2]=data[fileparts[l]:fileparts[l+1],:].real;
  #bipData[:,1::2]=data[fileparts[l]:fileparts[l+1],:].imag;
  bipData[:,0::2]=data.real;
  bipData[:,1::2]=data.imag;
  fout.write( bipData.astype(np.dtype(numpy.float32)) );
fout.close();
A.modifyResults('m_crop', 'Data_output_file', mobj.crop.Data_output_file+'.cr4');
A.modifyResults('m_crop', 'Data_output_format', 'complex_real4')

