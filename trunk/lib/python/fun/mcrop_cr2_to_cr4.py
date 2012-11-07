data=adore.getdata(mobj.crop.Data_output_file,(mobj.crop.Last_pixel-mobj.crop.First_pixel+1), 'cr2', (mobj.crop.Last_line-mobj.crop.First_line+1));
adore.writedata(mobj.crop.Data_output_file+'.cr4', data, 'cr4')
A.modifyResults('m_crop', 'Data_output_file', mobj.crop.Data_output_file+'.cr4');
A.modifyResults('m_crop', 'Data_output_format', 'complex_real4')
