#!/bin/bash

txtf=${1}
htmlf=${2}

rm ${htmlf}/links.html
for file in `ls ${1} | grep -v "~"`;
do 
 echo "<a href=${file}.html>${file}</a><br>" >> ${htmlf}/links.html 
 echo "<a href=links.html>Back to List</a>" > ${htmlf}/${file}.html
 sed '/^[[:space:]]*$/d' ${txtf}/${file} >> ${htmlf}/${file}.html
 ./replaceText.sh ${htmlf}/${file}.html txt2html.filter
 echo "<BR><a href=links.html>Back to List</a>" >> ${htmlf}/${file}.html
done
