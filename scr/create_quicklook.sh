#!/bin/bash
# Usage:
# $0 FileNameRegExp CPXFIDDLEoptions

`ls $1 > temporary.file`
for file in `cat temporary.file`
do
	len=${#file}
	res_file=`echo ${file:0:$((${len}-3))}res`
	num_of_pixels=`cat ${res_file} | grep "Number of pixels (multilooked):" | tail -n1 | cut -f 2 -d :| tr -d [:blank:]`
	cmd="/RAID6/insar_lab/doris_3.18.cstars/cpxfiddle -w ${num_of_pixels} $2 $file > ${file}.ras"
	echo $cmd
	echo $cmd >> temporary.file2
	#`$cmd`
done
rm temporary.file
/bin/sh temporary.file2
#rm temporary.file2
