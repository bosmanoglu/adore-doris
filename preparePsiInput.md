# USAGE: #
```
      p preparePsiInput.adr
      p preparePsiInput.adr outputFileName i12sType
```
# DESCRIPTION: #
> preparePsiInput.adr is an ADORE script.

> It prepares the psi-input file for the TU-DELFT PSI-Toolbox.

# INPUT: #
> outputFileName: File name for the output. (Default: psi\_input.txt)

> i12sType: Type of the interferogram to be used. Currently srp (subtrefpha,
> > subtract\_reference\_phase) or srd (subtrrefdem, subtract\_reference\_dem)
> > can be given. (Default: srp).

# OUTPUT: #

> Lists processed i12s folders, and creates the output file (psi\_input.txt).