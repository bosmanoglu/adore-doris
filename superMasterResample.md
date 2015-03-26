# USAGE: #
```
    superMasterResample superMaster [scene]
```
# DESCRIPTION: #
> superMasterResample is an internal ADORE command. <br>
<blockquote>It resamples all crops to a single master image, so that the resulting files can be used to combine interferograms among any pair without resampling. <br></blockquote>

<blockquote>If a DEM is available it is equivalent to running:<br>
<blockquote><code>settings apply -r -q int_multilook=\"1 1\" srp_multilook=\"1 1\" crd_include_fe=on;coarseorb;coarsecorr;fine;coregpm;resample;interfero; comprefdem;addrefpha2s_crop</code><br></blockquote></blockquote>

<blockquote>If a DEM is not available it is equivalent to running:<br>
<blockquote><code>settings apply -r -q int_multilook=\"1 1\" srp_multilook=\"1 1\" srp_dumprefpha=on;coarseorb;coarsecorr;fine;coregpm;resample;interfero; comprefpha;subtrrefpha;addrefpha2s_crop</code><br></blockquote></blockquote>

<h1>INPUT:</h1>
<blockquote>superMaster: the name of the folder in the data file to be used as the resampling master.</blockquote>

<blockquote><h2>OPTIONAL:</h2>
<blockquote><code>[scene]</code>: Specify a single scene to be resampled, instead of using all the <code>scenes include</code>d in the project.</blockquote></blockquote>


<h1>OUTPUT</h1>
<blockquote>Creates the <code>resample</code> folder inside the <code>${runFolder}</code> and resamples all crops listed in <code>scenes include</code>