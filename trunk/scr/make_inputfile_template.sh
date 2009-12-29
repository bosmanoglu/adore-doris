#!/bin/bash
#Modified By
##Batuhan Osmanoglu
###CSTARS 2007

# DO not forget to generate a slave_list file, using something like:
# ls -F ../../data/ | grep "/" | tr -d "/" > slave_list
# And do not forget to remove the master from slave_list.


frame=FRAME_NAME
crop=CROP_NAME
raid=RAID_DRV
username=USERNAME
master=MASTER_ORBIT_NR
echo "Finished defining variables."

proc=/${raid}/data/${username}/${frame}/process/${crop}
outputfile=inputfile_${frame}_${crop}.txt

echo "Output File: ${outputfile}"

for slave in `cat slave_list`
do
  ifg=${master}_${slave}
  ifg2=${master}_${slave}
  file=${proc}/${ifg}/${ifg2}.res

 
  if [ -f ${proc}/${ifg}/${ifg2}.srp ]
  then
  
    echo $ifg
    Btemp=`grep temp $file | sed 's/.*://; s/\/\/.*//'`
   # Btemp=`grep temp $file | sed 's/\/\/ Temporal baseline//' | sed 's/.*\ //; s/\ .*//'`
    slc=${proc}/${ifg}/${slave}.rsmp
    interf=${proc}/${ifg}/${ifg2}.srp
    h2ph=${proc}/${ifg}/${ifg2}.h2ph
    atmo=${proc}/${ifg}/${ifg2}.atmo
    echo ${slave} ${slc} ${interf} ${h2ph} ${atmo} ${Btemp} >> $outputfile
  fi

done


