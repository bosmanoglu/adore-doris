# USAGE: #
`      p singleMasterStack_Parallel.adr `

# DESCRIPTION: #
> singleMasterStack\_Parallel.adr is an ADORE script.

> It generates a single master stack interferograms using the ADORE settings.
> It is very similar to the singleMasterStack.adr script. However, this script
> uses the Torque-PBS system to distribute jobs to other computers.

# INPUT: #
> There are no input parameters.

# OUTPUT: #
> Creates ${projectFolder}/process/${runName}/ and processes crops & interferograms
> It runs the following DORIS steps:

> For crops: s\_readfiles, s\_porbits, s\_crop, s\_ovs

> For i12s: coarseorb, coarsecorr, fine, coregpm, coregpm, resample, interfero, comprefpha, subtrrefpha