#!/bin/bash
# Replace Text
# replacetext.sh textfile filterfile
#
# textfile: The file where the text will be read used. 
# filterfile: The file where several filters are listed 
#   for search and replace. 
#
txtf=${1}
fltf=${2}

OIFS=${IFS}
IFS=$'\n'
for pair in `cat ${fltf}`
do
  search=${pair%,*}
  replace=${pair##*,}
  #echo search:$search replace:${replace}
  sed -i ":begin;$!N;s@${search}@${replace}@g;tbegin" ${txtf}
done
IFS=${OIFS}
