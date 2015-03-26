# USAGE: #
```
 coarsecorr
```
# DESCRIPTION: #
> COARSECORR is an ADORE process and it runs the DORIS step with the same name.
> The offset in line (azimuth) and pixel (range) direction between master and slave is computed with an accuracy of about 1 pixel (1 offset for whole image).

> ADORE also supports a manual coregistration routine. You can access that by setting the `cc_method=manual`. ADORE will display the master and slave crop amplitudes. You can zoom in and pan the image. Then select the same point on both images using left click. Points are "recorded" using a right click on one of the windows. After both windows are closed, ADORE calculates the offsets and writes it to the result file.

# INPUT: #
> There are no required input parameters for this command.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #

> SUCCESS is printed to STDOUT on successful completion of process.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/scr/process/coarsecorr
 ${ADOREFOLDER}/drs/${dorisVersion}/coarsecorr.drs
 http://doris.tudelft.nl/usermanual/node49.html
```
# EXAMPLE: #
```
 coarsecorr
 coarsecorr -M10/10 (only when cc_method=manual)
```
# KNOWN BUGS: #
> With the manual method, if the crops are large, and you run out of memory trying to display them try adding the multilooking option (-M).