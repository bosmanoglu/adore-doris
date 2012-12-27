import insar
baselines_file=os.path.join(setobj.adore.baselinesfolder.strip('"'), 'baselines')
master=insar.time_series.select_single_master_from_baselines(baselines_file)
fp=open(setobj._ipy_.pipe, "w")
fp.write("%s\n" % master)
fp.close()
