off=np.loadtxt(os.path.join(setobj.adore.outputfolder.strip('"'),'manual_offsets_cc.txt'));
if isvector(off):
  print "Please select more points. Manual offset calculation failed."
else:  
#  iobj.coarse_correl.Coarse_correlation_translation_lines=(off[:,0]-off[:,2]).mean()-mobj.crop.First_line;   #Average offset in azimuth
#  iobj.coarse_correl.Coarse_correlation_translation_pixels=(off[:,1]-off[:,3]).mean()-mobj.crop.First_pixel; #Average offset in range
  iobj.coarse_correl.Coarse_correlation_translation_lines=int(round( ((off[:,0]-off[:,2])*off[:,4]).sum()/sum(off[:,4])))-mobj.crop.First_line;   #Average offset in azimuth
  iobj.coarse_correl.Coarse_correlation_translation_pixels=int(round( ((off[:,1]-off[:,3])*off[:,4]).sum()/sum(off[:,4])))-mobj.crop.First_pixel; #Average offset in range
  iobj.coarse_correl.Number_of_correlation_windows='%d of %d' % (off.shape[0],off.shape[0])
  iobj.coarse_correl.results=np.zeros([off.shape[0],6])
  iobj.coarse_correl.results[:,0]=np.r_[1:off.shape[0]+1]
  iobj.coarse_correl.results[:,1]=off[:,0]
  iobj.coarse_correl.results[:,2]=off[:,1]
  iobj.coarse_correl.results[:,3]=off[:,4] #np.ones([1,off.shape[0]])*0.99
  iobj.coarse_correl.results[:,4]=off[:,0]-off[:,2]
  iobj.coarse_correl.results[:,5]=off[:,1]-off[:,3]
  A.addResults('coarse_correl', iobj.coarse_correl);  


