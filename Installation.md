# Live DVD #
You can download ADORE Live DVD which comes with:
  * Ubuntu 12.04 LTS
  * ADORE-DORIS (0.1.416)
  * DORIS (4.04.4)
  * SNAPHU
  * GMT, GDAL, IMAGEMAGICK from Ubuntu Repositories.

The DVD is available here:

http://www.osmanoglu.org/sar/98-live-dvd-for-adore-doris

Simply download and burn the `iso` image on a DVD as a DVD image (NOT as a file/data dvd) and start your computer from the DVD drive.

# From EO-Tools Repository #
You can add the EO-Tools repository to your apt-sources and get the following packages: `adore-doris, doris, getorb, snaphu`<br>
Thanks to <b>Antonio Valentino</b> for packaging these applications.<br>
<br>
To add the repository:<br>
<code>sudo add-apt-repository ppa:a.valentino/eotools</code>

Update the package list:<br>
<code>sudo apt-get update</code>

To install adore-doris (this should also install doris, getorb and snaphu)<br>
<code>sudo apt-get install adore-doris</code>

<h1>Installing DORIS and Snaphu From Ubuntu and Debian Repositories</h1>
by Antonio Valentino and Francesco P. Lovergine on July 18th, 2013.<br>
<br>
We finally have doris and snaphu in debian:<br>
<ul><li><a href='http://packages.debian.org/sid/doris'>http://packages.debian.org/sid/doris</a>
</li><li><a href='http://packages.debian.org/sid/snaphu'>http://packages.debian.org/sid/snaphu</a></li></ul>

Currently they are only available in the unstable (sid) and testing (jessie) archives, not in stable (wheezy).<br>
You need to enable the <code>contrib</code> and <code>non-free</code> archives in your <code>/etc/apt/source.lists</code> in order be able to install them.<br>
<br>
Also these packages will be in Ubuntu 13.10 (saucy) in the <code>multiverse</code> archive.<br>
<br>
<h1>Debian Package Installation</h1>
You can download and install the Debian packages under Debian based operating systems including Ubuntu.<br>
<br>
Packages are available here: <a href='http://code.google.com/p/adore-doris/downloads/list'>http://code.google.com/p/adore-doris/downloads/list</a>

Once downloaded use your favorite package manager (or simply double-click) on the package file. After the installation is complete you can run adore in a terminal window.<br>
<br>
<h1>Manual Installation of Latest Development Version</h1>

ADORE consists of bash shell scripts and has a simple setup.<br>
<br>
ADORE-DORIS installation consists of three steps.<br>
<ul><li>Dependencies: Installation of dependencies.<br>
</li><li>SVN-Checkout: Checking out latest ADORE-DORIS from the svn. See instructions at: <a href='http://code.google.com/p/adore-doris/source/checkout'>http://code.google.com/p/adore-doris/source/checkout</a>
</li><li>Setup: Setting your path to point to ADORE-DORIS executables (scr) directory.</li></ul>

<h2>Dependencies</h2>

<b>Bold</b> text indicates packages are required for ADORE-DORIS to have some functionality. Optional packages are indicated by <i>italics</i> and they expand the capabilities of ADORE-DORIS. Missing optional packages might cause error messages if a dependent command is issued (for example, if you do not have GDAL and use SAVEAS).<br>
<br>
Code blocks such as <code> code-block </code> show the command line to install mentioned packages on Ubuntu systems.<br>
<br>
ADORE requires the following packages to be installed on your system:<br>
<ul><li><b>TU-DELFT DORIS</b> <a href='http://enterprise.lr.tudelft.nl/doris/'>http://enterprise.lr.tudelft.nl/doris/</a>
<blockquote>TU-DELFT DORIS is used for all interferometric processing.<br>
</blockquote></li><li><b>GMT</b> <a href='http://gmt.soest.hawaii.edu/'>http://gmt.soest.hawaii.edu/</a> <code>sudo apt-get install gmt</code>
<blockquote>GMT is required for TU-DELFT DORIS and ADORE-DORIS uses it in MASK and SAVEAS commands.<br>
</blockquote></li><li><b>ipython</b> <a href='http://ipython.org'>http://ipython.org</a> <code>sudo apt-get install ipython</code>
<blockquote>ipython is required to provide ADORE specific improvements to DORIS (e.g. TanDEM-X bistatic processing, manual coarse offset calculation, network deramping of wrapped data, selecting interferometric pairs and etc.) Furthermore ipython allows ADORE to open the current interferogram in python for interactive calculations and data visualization.<br>
</blockquote></li><li><b>Python modules</b> <code>sudo apt-get install python-numpy python-scipy python-mpltoolkits.basemap</code>
<blockquote>Several python modules are used in ADORE python scripts to assist processing and visualization.<br>
</blockquote></li><li><i>GNUPLOT</i> <a href='http://www.gnuplot.info/'>http://www.gnuplot.info/</a> <code>sudo apt-get install gnuplot</code>
<blockquote>GNUPLOT is used after the BASELINES command to create a post-script (PS) image of the temporal and perpendicular baselines.<br>
</blockquote></li><li><i>Image-Magick</i> <a href='http://www.imagemagick.org/'>http://www.imagemagick.org/</a> <code>sudo apt-get install imagemagick </code>
<blockquote>Image-Magick is optional, it allows RASTER command to convert images from sun-raster format to supported formats (png, jpg, etc.).<br>
</blockquote></li><li><i>GDAL</i> <a href='http://www.gdal.org/'>http://www.gdal.org/</a> <code>sudo apt-get install gdal-bin</code>
<blockquote>GDAL is optional, it allows ADORE-DORIS outputs to be exported to ArcGIS via SAVEAS command.</blockquote></li></ul>


The packages below are requirements for Agooey (ADORE-GUI):<br>
<ul><li><b>pygtk</b> <code>sudo apt-get install python-gtk2</code>
</li></ul><blockquote>Required to display Agooey window.<br>
</blockquote><ul><li><b>vte</b> <code>sudo apt-get install python-vte</code>
</li></ul><blockquote>Virtual Terminal Emulator is used to display the ADORE prompt.<br>
</blockquote><ul><li><i>ipython-qtconsole</i> <code>sudo apt-get install ipython-qtconsole</code>
</li></ul><blockquote>In Agooey, ipython can be opened in a separate window, releasing ADORE prompt for processing. If qtconsole is not available ipython opens inside vte.</blockquote>

<h2>Setup</h2>
ADORE-DORIS scripts folder needs to be in your environment PATH. You can do this in ubuntu systems by adding the following lines to the end of your ~/.bashrc file.<br>
<br>
<pre><code>export ADORESCR=/path/to/adore-doris/scr<br>
export PATH=${PATH}:${ADORESCR}<br>
</code></pre>