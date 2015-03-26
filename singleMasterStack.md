# USAGE: #
`      p singleMasterStack.adr `

# DESCRIPTION: #
> singleMasterStack.adr is an ADORE script.

> It generates a single master stack interferogram using the ADORE settings.

# INPUT: #
> There are no input parameters.

# OUTPUT: #
> Creates ${projectFolder}/process/${runName}/ and processes crops & interferograms

> It runs the following DORIS steps:

> For crops: s\_readfiles, s\_porbits, s\_crop, s\_ovs

> For i12s: coarseorb, coarsecorr, fine, coregpm, coregpm, resample, interfero, comprefpha, subtrrefpha