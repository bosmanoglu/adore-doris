# USAGE: #
```
 slant2htrick
```
# DESCRIPTION: #
> SLANT2HTRICK is an internal ADORE function.
> It creates DORIS slant2h output from comprefdem. This function calls the
ADORE function dem2slant2h.
# INPUT: #
> There are no required input parameters for this command.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #

> Adds slant2h step to ${i\_resfile} and creates a symbolic link from the
${crd\_out\_dem\_lp} to ${s2h\_out\_hei}.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/scr/fun/dem2slant2h
```
# EXAMPLE: #
```
 slant2htrick
```
# KNOWN BUGS: #
> None.