#!/bin/bash
SVNFOLDER="/home/bosmanoglu/projectLocker/adore-doris"
#
rm -rf /tmp/adore/
svn export ${SVNFOLDER} /tmp/adore/
# rm unwanted directories
rm -rf /tmp/adore/build
rm -rf /tmp/adore/gui
#get version
version=${1}
cat > adore.list <<_EOF
\$prefix=/opt/adore
\$exec_prefix=\${prefix}
\$bindir=\${exec_prefix}/bin
\$srcdir=.
%product ADORE - Automated DORIS Environment
%copyright 2009-2011, Batuhan Osmanoglu.
%vendor Batuhan Osmanoglu
%license LICENSE
%readme README
%description ADORE is a shell environment designed to simplify and streamline interferometry with DORIS.
%version ${version}
%requires gmt
%requires gnuplot
%requires imagemagick
%requires gdal-bin

_EOF
mkepmlist -g root -u root --prefix /opt/adore /tmp/adore/ >> adore.list
echo "l 000 root root /usr/bin/adore /opt/adore/scr/adore" >> adore.list
cd ${SVNFOLDER}/build
sudo epm -a all -f deb adore
