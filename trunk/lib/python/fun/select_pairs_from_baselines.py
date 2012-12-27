import insar
baselines_file=os.path.join(setobj.adore.baselinesfolder.strip('"'), 'baselines')
pairs=insar.time_series.select_pairs_from_baselines(baselines_file, btemp_limits=[0,float(setobj._ipy_.t)], bperp_limits=[0,float(setobj._ipy_.p)])
savetxt(setobj._ipy_.f, pairs[:], delimiter=',', fmt='%s')
