# USAGE: #
```
	s dorisProcess
	s variableName
```
# DESCRIPTION: #
> s is a builtin ADORE command.  <br>
<blockquote>It can show the input file for the given DORIS processing step. It can also be used to display ADORE variables.</blockquote>

<h1>INPUT:</h1>
<blockquote><code>dorisProcess</code>: Name of the DORIS processing step to run. List of available<br>
<blockquote>processes can be found at the end of this help message or using lsprocess<br>
whenever required.</blockquote></blockquote>

<blockquote><code>variableName</code>: Name of the DORIS setting (ADORE variable) to display. This<br>
<blockquote>can be a partial name. For example if given m<i>as variable name ADORE will<br>
display all variables and their values starting with m</i></blockquote></blockquote>


<h1>OUTPUT:</h1>
<blockquote>Dumps input file for the given step to the stdout.</blockquote>

<h1>Example:</h1>
<pre><code>ADORE: s rs_<br>
rs_az_buffer=200<br>
rs_dbow=0 0 0 0<br>
rs_dbow_geo=19.7023 -101.1955 4000 1000<br>
rs_method=knab6p<br>
rs_out_file=/RAID1/batu/playGround/fcigna_Morelia/process/parallel/i12s/050122_050507/050507.rs<br>
rs_out_format=cr4<br>
rs_rg_buffer=200<br>
rs_shiftazi=on<br>
<br>
ADORE: s resample<br>
screen info //<br>
beep off //<br>
batch on //<br>
overwrite on //<br>
preview off // sunraster files with cpxfiddle<br>
listinput on // copy this file to log<br>
memory 500 // mb<br>
<br>
logfile /RAID1/batu/playGround/fcigna_Morelia/process/parallel/i12s/050122_050507/parallel.log //<br>
m_resfile /RAID1/batu/playGround/fcigna_Morelia/process/parallel/i12s/050122_050507/050122.res //<br>
s_resfile /RAID1/batu/playGround/fcigna_Morelia/process/parallel/i12s/050122_050507/050507.res //<br>
i_resfile /RAID1/batu/playGround/fcigna_Morelia/process/parallel/i12s/050122_050507/050122_050507.res //<br>
<br>
orb_interp polyfit //<br>
dumpbaseline 1 1 // eval baseline on grid<br>
height 2230 // average height for the crop<br>
tiepoint 0.0 0.0 0.0 //<br>
m_rg_t_error 0.0 //<br>
m_az_t_error 0.0 //<br>
s_rg_t_error 0.0 //<br>
s_az_t_error 0.0 //<br>
<br>
process resample //<br>
<br>
rs_method knab6p //<br>
rs_out_file /RAID1/batu/playGround/fcigna_Morelia/process/parallel/i12s/050122_050507/050507.rs //<br>
rs_out_format cr4 //<br>
rs_dbow 0 0 0 0 //<br>
rs_dbow_geo 19.7023 -101.1955 4000 1000 //<br>
rs_shiftazi on //<br>
<br>
stop<br>
<br>
</code></pre>