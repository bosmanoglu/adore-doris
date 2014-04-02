data=adore.getdata(sobj.crop.Data_output_file,(sobj.crop.Last_pixel-sobj.crop.First_pixel+1), 'cr2', (sobj.crop.Last_line-sobj.crop.First_line+1));

filesize=os.path.getsize(sobj.crop.Data_output_file);
width=sobj.crop.Last_pixel-sobj.crop.First_pixel+1;
datatype, complexFlag=adore.dataFormat2dataType('cr2');
length=float(filesize)/width/np.dtype(datatype).itemsize/2; 
fileparts=fix(linspace(0, length, 10));
  
#adore.writedata(sobj.crop.Data_output_file+'.cr4', data, 'cr4')
fout=open(sobj.crop.Data_output_file+'.cr4', 'wb');
for l in xrange(len(fileparts)-1):
  bipData=np.empty([fileparts[l+1]-fileparts[l], data.shape[1]*2]);
  bipData[:,0::2]=data[fileparts[l]:fileparts[l+1],:].real;
  bipData[:,1::2]=data[fileparts[l]:fileparts[l+1],:].imag;
  fout.write( bipData.astype(np.dtype(numpy.float32)) );
fout.close();

A.modifyResults('s_crop', 'Data_output_file', sobj.crop.Data_output_file+'.cr4');
A.modifyResults('s_crop', 'Data_output_format', 'complex_real4')
