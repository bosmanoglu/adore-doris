# DESCRIPTION: #
M\_FBD2FBS is an ADORE process and it runs the DORIS oversampling (m\_ovs) step in range dimension for ALOS fine beam dual polarization (FBD) images to match the resolution of fine beam single polarization (FBS) imagery.

This function only runs for ALOS imagery with a "Total\_range\_band\_width" of 14 MHz and will do nothing for ALOS FBS imagery, which is 28 MHz. Therefore it is safe to use with the [crops](crops.md) command.

This function will backup the original master result file with the `.bck` suffix. After the processing the crop step in the new output will point to the oversampled file. The oversample step is removed from the result file with the undo command to allow further oversampling of the data is necessary.

# INPUT: #
> There are no required input parameters for this command.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #

> ${master}.ovs file is created.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/drs/${dorisVersion}/m_ovs.drs
 http://doris.tudelft.nl/usermanual/node33.html
```
# EXAMPLE: #
```
 m_fbd2fbs
```
# KNOWN BUGS: #
> None.