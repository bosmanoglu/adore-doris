#!/bin/bash

wikif=${1}
txtf=${2}

for file in `ls ${1} | grep -v "~"`;
do 
 #sed '/^[[:space:]]*$/d' ${wikif}/${file} >> ${txtf}/${file}
 tail -n +3 ${wikif}/${file} >> ${txtf}/${file%%.wiki}
 ./replaceText.sh ${txtf}/${file%%.wiki} wiki2txt.filter
done

#rm unnecessary pages
for f in "PageName TipsAndTricks Scripts Polls FAQ adoreFunctionsAndScripts Roadmap Reference Other_SAR_Software Functions sidebar"
do 
  rm ${txtf}/${f}
done
