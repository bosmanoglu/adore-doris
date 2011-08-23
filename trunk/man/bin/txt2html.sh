#!/bin/bash

txtf=${1}
htmlf=${2}

rm ${htmlf}/links.html
for file in `ls ${1}`;
do 
 echo "<a href=${file}.html>${file}</a><br>" >> ${htmlf}/links.html 
 cp ${txtf}/${file} ${htmlf}/${file}.html
 ./replaceText.sh ${htmlf}/${file}.html txt2html.filter
 echo "<a href=links.html>Functions</a>" >> ${htmlf}/${file}.html
done
