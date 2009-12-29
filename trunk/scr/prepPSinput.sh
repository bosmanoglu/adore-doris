#!/bin/bash
###############################################
###############################################
# prepPSinput.sh
# Part of Adore Project
# Batuhan Osmanoglu, Sep 2007 CSTARS, Miami
#
#
# This function reads interferogram folders 
# and generates the file list required for PS.
#
#
# Requires:
#	- Location of Interferogram Folders
#	- Output FileName
# Provides:
#	- Output File
#
###############################################
###############################################

i12s_location=${1}
outputfile=${2}
outputfolder=`dirname ${outputfile}`
echo "prepPSinput.sh: Finished defining variables."

echo "prepPSinput.sh: Output File= ${outputfile}"

ls ${i12s_location} > tmp_folderlist

for i12s in `cat tmp_folderlist`
do
  master=`echo ${i12s} | cut -f1 -d_`
  slave=`echo ${i12s} | cut -f2 -d_`
  file=${i12s_location}/${master}_${slave}/${master}_${slave}.res

  if [ -f ${i12s_location}/${master}_${slave}/${master}_${slave}.srp ]
  then
  
    echo "prepPSinput.sh: Reading Interferogram ${master}_${slave}"
    Btemp=`grep temp $file | sed 's/.*://; s/\/\/.*//'`
   # Btemp=`grep temp $file | sed 's/\/\/ Temporal baseline//' | sed 's/.*\ //; s/\ .*//'`
    slc=${i12s_location}/${master}_${slave}/${slave}.rsmp
    interf=${i12s_location}/${master}_${slave}/${master}_${slave}.srp
    h2ph=${i12s_location}/${master}_${slave}/${master}_${slave}.h2ph
    atmo=${outputfolder}/run_N/${master}_${slave}.atmo
    echo ${slave} ${slc} ${interf} ${h2ph} ${atmo} ${Btemp} >> $outputfile
  fi

done

rm tmp_folderlist
echo "Do not forget to modify foldername for ATMO files"


