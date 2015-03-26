# USAGE: #
```
	s_crop2resample
```
# DESCRIPTION: #
> S\_CROP2RESAMPLE is an internal ADORE command.
> It is used in creating interferograms coregistered to a different scene,
> as needed in Small Baselines (SBAS) interferometry.
> s\_crop2resample copies the result of m\_ovs or the m\_crop as s\_resample
> and changes the data\_output\_file to the s\_crop(or s\_ovs) output file.
> Selection between ovs and crop is done automatically. If m\_ovs is in the
> process control flag, ovs is used. Otherwise m\_crop is used.
> Master and Slave should be processed in the same way. They both have to
> be oversampled or not.
# INPUT: #
> There are no required input parameters for this command.
# OUTPUT #
> > Modifies the result file by copying the m\_crop(m\_ovs) to s\_resample