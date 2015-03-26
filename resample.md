# USAGE: #
```
 resample
```
# DESCRIPTION: #
> RESAMPLE is an ADORE process and runs the DORIS step with the same name.
> The slave image is resampled (reconstruction of original signal from the
> samples by correlation with interpolation kernels in space domain)
> accordingly to the transformation model from the step COREG\_PM and
> optionally DEMASSIST. This model states with sub-pixel accuracy which points
> of the slave correspond to the master grid.
> Note: This step may be fairly time consuming.
# INPUT: #
> There are no required input parameters for this command.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #

> ${slave}.rs file is generated.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/drs/${dorisVersion}/resample.drs
 http://doris.tudelft.nl/usermanual/node79.html
```
# EXAMPLE: #
```
 resample
```
# KNOWN BUGS: #
> None.