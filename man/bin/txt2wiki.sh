#!/bin/bash

txtf=${1}
wikif=${2}

for file in `ls ${1} | grep -v "~"`;
do 
 echo "#summary ${file}" > ${wikif}/${file}.wiki
 echo "#labels Phase-Support,Help"  >> ${wikif}/${file}.wiki
 sed '/^[[:space:]]*$/d' ${txtf}/${file} >> ${wikif}/${file}.wiki
 ./replaceText.sh ${wikif}/${file}.wiki txt2wiki.filter
done
