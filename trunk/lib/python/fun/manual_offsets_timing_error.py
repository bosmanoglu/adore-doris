off=np.loadtxt(os.path.join(setobj.adore.outputfolder.strip('"'),'manual_offsets.txt'));
if isvector(off):
  print "Please select more points. Manual Timing calculation failed."
else:  
  mobj.master_timing.Coarse_correlation_translation_lines=(off[:,0]-off[:,2]).mean(); #Average offset in azimuth
  mobj.master_timing.Coarse_correlation_translation_pixels=(off[:,1]-off[:,3]).mean(); #Average offset in range
  mobj.master_timing.Master_azimuth_timing_error=-mobj.master_timing.Coarse_correlation_translation_lines/mobj.readfiles.Pulse_Repetition_Frequency;
  mobj.master_timing.Master_range_timing_error=-mobj.master_timing.Coarse_correlation_translation_pixels/(2*mobj.readfiles.Range_sampling_rate*1e6);
  mobj.master_timing.Correlation_method='manual'
  mobj.master_timing.Number_of_correlation_windows_used='%d of %d' % (off.shape[0],off.shape[0])
  A.addResults('m_timing', mobj.master_timing);


