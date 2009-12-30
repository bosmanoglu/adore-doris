#!/bin/bash
#  Modif. Batu 2006/11/17 02:03pm
# baseline.fast
#%// BK 27-Oct-2000
#%// $Revision: 3.5 $  $Date: 2003/04/14 06:35:15 $
######################################################################
#set -v on
#set -x on
PRG=`basename "$0"`
VER="v1.1, FMR software"
AUT="Bert Kampes, (c)2000 \n Batuhan Osmanoglu, CSTARS 2007"
echo "$PRG $VER, $AUT"

### Handle input
if [ $# != 2 ]; then
	echo " Usage: $0 project_inputfile baseline_filename_pattern"
	exit 127
fi

# PROJECT PARAMATERS: global & only these need to be modified
ProjectFolder=${1}
baselinepattern=${2}
# DATE_REFERENCE: 
# for getorb UTC seconds since [00:00:00 1970-01-01] to [00:00:00
# 1985-01-01]
#date_getorb_ref=`date --date '01-Jan-1985 0:00:00' +%sm`
# FUNCTION: LSD: list only directory (requests (g)awk)
#lsd ()
#{
#    # local argument
#        ls -l ${1} | awk '/^d/ {print $NF}'
#}
         
# CREATE INPUT FILES: easier with input/output files
#lsd ${baselinepattern} > ${ProjectFolder}/temp/folder.list
#folder_list=`ls ${ProjectFolder}/temp/baseline_*_I.res` # > ${ProjectFolder}/temp/folder.list      
find ${ProjectFolder} -nowarn -name "${baselinepattern}" > ${ProjectFolder}/temp/baselinefile.list
baselinefile_list=`cat ${ProjectFolder}/temp/baselinefile.list`

#Clean Start
if [ -e ${ProjectFolder}/temp/baselines.txt ]; then
	echo "Renaming file as ${ProjectFolder}/temp/baselines.txt.old"
	mv ${ProjectFolder}/temp/baselines.txt ${ProjectFolder}/temp/baselines.txt.old
fi
printf "Frame Btemp Bpar\n" > ${ProjectFolder}/temp/baselines.txt

# Initialize average values and folder counter
btemp_avg=0;
bperp_avg=0;
cntr=0;
for baselinefile in ${baselinefile_list}
  do
  echo "Reading ${baselinefile}"
  #resultfile=`ls ${ProjectFolder}/process/crops/${folder}/*_${folder}.res`
  resultfile=${baselinefile}
  ### Check if ls is successful.. If not put 0 0...
  if [ -f ${resultfile} ]; then
  	#echo "Found Resultfile: ${resultfile}"
  	### Correct input.
  	btemp=`cat ${resultfile} | grep Btemp | cut -f2 -d: | cut -f1 -d/ | tr ' ' ' '`
  	bperp=`cat ${resultfile} | grep Bperp | cut -f2 -d: | cut -f1 -d/ | tr ' ' ' '`
  	
  	btemp_avg_new=$(echo "scale=2; ${btemp_avg}+${btemp}" | bc )
  	if [ -z ${btemp_avg_new} ]; then
  		echo "Error Reading Btemp from ${resultfile}"
  		echo ${resultfile} >> ${ProjectFolder}/excludeslc
  		continue	### Skip this file
  	else
  		btemp_avg=${btemp_avg_new}
  	fi
  	
  	bperp_avg_new=$(echo "scale=2; ${bperp_avg}+${bperp}" | bc )
  	if [ -z ${bperp_avg_new} ]; then
  		echo "Error Reading Bperp from ${resultfile}"
  		echo ${resultfile} >> ${ProjectFolder}/excludeslc
  		continue	### Skip this file
  	else
  		bperp_avg=${bperp_avg_new}
  	fi
  	let cntr+=1;
  	#line=$(printf "%s\t%s\t%s" ${resultfile} $btemp $bperp )
  	line=`echo ${resultfile} $btemp $bperp`
	echo ${line}
  	echo $line >> ${ProjectFolder}/temp/baselines.txt	  
  else
  	echo "Can not find Resultfile: ${resultfile}"
  	line=$(printf "%s\t%s\t%s" ${resultfile} "0 0" )
  	echo $line >> ${ProjectFolder}/temp/baselines.txt
  fi
done

btemp_avg=$(echo "scale=2; ${btemp_avg}/${cntr}" | bc)
bperp_avg=$(echo "scale=2; ${bperp_avg}/${cntr}" | bc)

echo "DEBUG:  AVG_Temp:${btemp_avg} AVG_Perp:${bperp_avg}"
exec < ${ProjectFolder}/temp/baselines.txt
read line	## Skip Header
unset mintotal
while read line
  do
	file=`echo ${line} | cut -f1 --delimiter=" "`
	btemp=`echo ${line} | cut -f2 --delimiter=" "`
	bperp=`echo ${line} | cut -f3 --delimiter=" "`
	
##	echo "DEBUG: F:${folder} T:${btemp} P:${bperp}"
	ratio=$(echo "scale=2; ${bperp_avg}/(2*${btemp_avg})" | bc )
	weighted_btemp=$(echo "scale=3;(${btemp} - ${btemp_avg})/(2*${btemp_avg})" | bc )
	weighted_bperp=$(echo "scale=3;(${bperp} - ${bperp_avg})/${bperp_avg}" | bc )
	weighted_total=$(echo "scale=3;sqrt( ${weighted_btemp}^2 + ${weighted_bperp}^2 )" | bc)
	if [ ! ${min_total} ]; then	##If not defined yet, give min_total a value.
		min_total=${weighted_total}
#		echo "min total defined"
	elif [ `echo "${weighted_total} < ${min_total}" | bc` == 1  ]; then
#		echo "changing min total" `echo "${weighted_total} < ${min_total}" | bc`
		min_total=${weighted_total}
		master=${file}
	fi
	echo "Folder:" ${file} "Total:"${weighted_total} "Current Min:"${min_total} 
  done
#master=echo $master |cut -f 2 -d "_"
echo $min_total $master

rm -f ${ProjectFolder}/temp/tmp.project.set
exec < ${ProjectFolder}/temp/project.set
while read line
  do
	parameter=`echo ${line} | cut -f1 --delimiter="="`
	value=`echo ${line} | cut -f2 --delimiter="="`

	echo $parameter = $value

	if [ $parameter == "MasterFolder" ]; then
		echo "MasterFolder="${master} >> ${ProjectFolder}/temp/tmp.project.set
		echo "Master = " ${master}
		continue
	fi
	echo ${line} >>${ProjectFolder}/temp/tmp.project.set	
  done
exit 0
