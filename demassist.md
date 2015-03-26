# USAGE: #
```
 demassist 
```
# DESCRIPTION: #
> DEMASSIST is an ADORE process which runs the DORIS step with the same name.
> The slave image is coregistered to the master image based on a DEM. For each pixel of the master image the corresponding (real valued) coordinate in the slave image is computed.
# INPUT: #
> There are no required input parameters for this command.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #
> > SUCCESS is printed to STDOUT on successful completion of process.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/drs/${dorisVersion}/demassist.drs
 http://doris.tudelft.nl/usermanual/node71.html
```
# EXAMPLE: #
```
  demassist 
```
# KNOWN BUGS: #
> > None.