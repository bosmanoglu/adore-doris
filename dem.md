# USAGE: #
```
	dem operation parameters
	dem make [SRTM1/SRTM3] [extraBufferPercentage] [name]
	dem load [path/to/demfile.dem]
	dem unload
	dem check 
        dem import path/to/demfile.dem "gdalOptions"
        dem extent
        dem expand path/to/big.dem [merged.bil]
        dem export format 
        dem view
```
# DESCRIPTION: #
> DEM is an internal ADORE command.
> It can generate and load DEM settings to the environment.
# INPUT: #
  * `dem`:<br>
<ul><li>defaults to "dem check"<br>
</li></ul><ul><li><code>dem make SRTM1/SRTM3 extraBufferPercentage name</code><br>
<ul><li>Calculates the master scene coverage and issues a call to<br>
</li></ul></li><li><code>construct_dem.sh</code>
<ul><li>Area if padded (enlarged) in all directions with the extraBufferPercentage. You can call this function with no/some arguments. Defaults are: <code>SRTM3 20 dem</code>
</li></ul></li><li><code>dem load path/to/demfile.dem</code><br>
<ul><li>Load's the specified dem file.<br>
</li></ul></li></ul><blockquote>Currently supported DEM formats:<br>
<ul><li>output of "dem make"<br>
</li><li>construct_dem.sh (from TU-DELFT).<br>
</li><li>ArcGIS .flt files (with .flt and .hdr files should be in the same folder and have the same name.)<br>
</li><li>ESRI .bil files (with .hdr files)<br>
</li><li>GMT .grd files. (Creates .dem and input_doris files in the current directory.)<br>
</li></ul></blockquote><ul><li><code>dem unload</code>:<br>
<ul><li>Clears sam_in_dem, dac_in_dem and crd_in_dem. If you want to re-run dem make this can be used.<br>
</li></ul></li><li><code>dem check</code>:<br>
<ul><li>Checks the environment DEM settings and suggests fixes to problems.<br>
</li></ul></li><li><code>dem import path/to/demfile.dem [gdalOptions]</code>:<br>
<ul><li>Converts and loads given DEM file using GDAL to ESRI BIL format (GDAL EHDR format). This function was used to be called <code>dem convert</code>.<br>
</li></ul></li><li><code>dem extent</code>:<br>
<ul><li>Calculates and displays the corner coordinates of the DEM based on input values.<br>
</li></ul></li><li><code>dem expand path/to/big.dem [merged.bil]</code>:<br>
<ul><li>Merge a small dem with a big dem. The small dem overwrites the big one.<br>
</li></ul></li><li><code>dem export format</code>:<br>
<ul><li>Export the current DEM in a different format. Currently only the following formats are available: <code>roipac, giant</code>.<br>
</li></ul></li><li><code>dem view</code>:<br>
<ul><li>Display DEM using <code>cpxview</code> and the input values. Additional options can be passed. See <code>? view</code></li></ul></li></ul>

<h1>OUTPUT:</h1>
<blockquote><code>dem make</code>: Generates a folder with the dem. Leaves the hgt files in the current folder.<br>
<code>dem load</code>: No outputs if success. Updates DORIS settings starting with <code>sam_</code>, <code>dac_</code>, and <code>crd_</code>.<br>
<code>dem unload</code>: Displays a text message indicating cleared variables.<br>
<code>dem check</code>: Checks and displays possible problems fixes on stdout.<br>
<h1>FILES and REFERENCES:</h1>
<pre><code> None.<br>
</code></pre>
<h1>EXAMPLE:</h1>
<pre><code>dem convert merapi_15m.asc "-s_srs '+proj=utm +zone=49M +ellps=WGS84 +datum=WGS84 +units=m +no_defs' "<br>
dem load merapi_15m.bil<br>
</code></pre>
<h1>KNOWN BUGS:</h1>
</blockquote><blockquote>If the merged DEM size is over 2GB the DEM expand command fails.