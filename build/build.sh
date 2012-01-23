#!/bin/bash
SVNFOLDER="/home/bosmanoglu/projectLocker/adore-doris"
#
rm -rf /tmp/adore/
svn export ${SVNFOLDER} /tmp/adore/
# rm unwanted directories
rm -rf /tmp/adore/build
#rm -rf /tmp/adore/gui
#Remove links
#rm -rf /tmp/adore/scr/agooey
#rm -rf /tmp/adore/scr/cpxview
#rm -rf /tmp/adore/drs/4.02
#rm -rf /tmp/adore/drs/4.06
#get version
version=`cat ${SVNFOLDER}/version`
cat > adore.list <<_EOF
\$prefix=/opt/adore
\$exec_prefix=\${prefix}
\$bindir=\${exec_prefix}/bin
\$srcdir=.
%product ADORE - Automated DORIS Environment
%copyright 2009-2011, Batuhan Osmanoglu.
%vendor Batuhan Osmanoglu
%maintainer Batuhan Osmanoglu <batuhan.osmanoglu@gmail.com>
%license LICENSE
%readme README
%description ADORE is a shell environment designed to simplify and streamline interferometry with DORIS.
%version ${version}
%requires gmt
%requires gnuplot
%requires imagemagick
%requires gdal-bin

_EOF
#Add adore link to system bin directory.
echo "l 000 root root /usr/bin/adore /opt/adore/scr/adore" >> adore.list
#Add links
#echo "l 000 root root /opt/adore/scr/agooey /opt/adore/gui/agooey" >> adore.list
#echo "l 000 root root /opt/adore/scr/cpxview /opt/adore/lib/python/cpxview.py" >> adore.list
#echo "l 000 root root /usr/bin/agooey /opt/adore/scr/agooey" >> adore.list
#echo "l 000 root root /opt/adore/drs/4.02 /opt/adore/drs/4.03" >> adore.list
#echo "l 000 root root /opt/adore/drs/4.06 /opt/adore/drs/4.05" >> adore.list
#create list
mkepmlist -g root -u root --prefix /opt/adore /tmp/adore/ >> adore.list
#Done replace links
cd ${SVNFOLDER}/build
sudo epm -a all -f deb adore
#sudo epm -a all -f rpm adore
