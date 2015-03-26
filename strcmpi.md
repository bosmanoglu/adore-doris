# USAGE: #
```
 strcmpi string1 string2
```
# DESCRIPTION: #
> STRCMPI is an ADORE function.
> It compares two strings inside ADORE in a case-insensitive fashion. 0 is
returned if the strings match. Otherwise 1 is returned.
# INPUT: #
> string1: First string to be matched.
> string2: Second string to be matched to first.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #

> Returns 0 if strings match.
> Returns 1 if strings do not match.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/scr/fun/functions
```
# EXAMPLE: #
```
 ADORE: strcmpi "adore" "ADORE" && echo "same" || echo "not same"
 same
 ADORE: strcmpi "ADORE" "ADORE" && echo "same" || echo "not same"
 same
 ADORE: strcmpi "ADORE1" "ADORE2" && echo "same" || echo "not same"
 not same
```
# KNOWN BUGS: #
None.