data=adore.getdata(sobj.crop.Data_output_file,(sobj.crop.Last_pixel-sobj.crop.First_pixel+1), 'cr2', (sobj.crop.Last_line-sobj.crop.First_line+1));
adore.writedata(sobj.crop.Data_output_file+'.cr4', data, 'cr4')
A.modifyResults('s_crop', 'Data_output_file', sobj.crop.Data_output_file+'.cr4');
A.modifyResults('s_crop', 'Data_output_format', 'complex_real4')
