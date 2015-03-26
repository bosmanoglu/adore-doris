# multiplePairs.adr #
## USAGE: ##
> `p multiplePairs.adr inputFile`

## DESCRIPTION: ##
> multiplePairs.adr is an ADORE script.
> It generates several interferograms whose master and slave orbits are defined by the input file.

INPUT:
> inputFile: A comma-separated-value file where each line indicates an
> > interferometric pair. First value defines the master and the second value defines the slave.
> > As an example file should have this format:
```
   masterScene1,slaveScene1
   masterScene2,slaveScene2
   ...
```
OUTPUT:

> Creates `${projectFolder}/process/${runName}/` and processes crops & interferograms
> It runs the following DORIS steps:
> > For crops: `m_readfiles;m_porbits;m_crop`
> > For i12s: `coarseorb;coarsecorr;fine;coregpm;resample;interfero;comprefpha;subtrrefpha;coherence`

# HOW-TO #
Guidelines for using multiplePairs.adr. <br>
Contributed by: Jiun-Yee Yen <br>
<a href='http://groups.google.com/group/adore-doris/msg/121321d4fe04bdd9'>http://groups.google.com/group/adore-doris/msg/121321d4fe04bdd9</a> <br>


<ul><li>copy multiplePairs.adr from your ADORE directory (mine is at: <code>/opt/adore/templates/multiplePairs.adr</code>) to your current working directory.</li></ul>

<ul><li>create a new file with dates of image pairs you want to process. Use <code>master_date01,slave_date01</code> without space before slave_date01. It’s essential that there’s no space before and after comma.</li></ul>

<ul><li>edit multiplePairs.adr for the steps you want to execute. Specifically, you need to edit the lines begin with <code>cropSteps</code> and <code>interferoSteps</code>.</li></ul>


<ul><li>If you have created a setting file already, then use <code>adore -u settings.set -i</code>. Otherwise, go into ADORE interactive environment with <code>adore -i</code>. Within the ADORE environment,  use <code>settings apply -r some_setting=some_value</code></li></ul>

<ul><li>issue: <code>p multiplePairs.adr pairs.txt</code>  in the ADORE environment.</li></ul>

That should create a directory named 'process'.  All the results will be in the respective directories within it.  If you want to see the results afterward, you can go into each individual image pair directory, load the setting file, and issue <code>raster p doris_step</code>.