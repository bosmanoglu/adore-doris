#!/bin/bash
# USAGE: 
#	construct_aster_dem.sh -n projectName -u username -p password -c category -f Localfolder -s stitchMethod W E S N
# 
# DESCRIPTION:
#	-n projectName: Specify a projectname for this DEM. The DEM will be generated inside a
#	 	folder with this name. (default="dem")
#	-u username: Your username for the Aster GDEM website.
#	-p password: Your password for the Aster GDEM website.
#	-c category: The category of science the data will be used. Available options are: 
#		disasters, health, energy, climate, water, weather, ecosystems, agriculture, 
#		or biodiversity
#	-f localFolder: Script will store downloaded Aster GDEM tiles in this folder. (default="./")
#		If you have all the tiles in the folder you can run this script without any username
#		password, category information. In that case no new tiles can be downloaded. 
#	-s stitchMethod: Choice of stitching methods. Default is 0.
#		stitchMethod 0 : No stitching, just download/unzip files
#		stitchMethod 1 : Using buildvrt and gdal_translate Doris readable (ENVI) output (Mahmut Arikan)
#		stitchMethod 2 : Using gdal_merge Doris readable (mff2) output(Petar Marinkovic)
#		stitchMethod 3 : Using gdal_merge Gtiff output (Petar Marinkovic)
#	W E S N: The corner coordinates of the study area. Enter West and South as - (negative)
#		values. Decimals are ignored maximizing the area (i.e. floor(west), ceil(east)) 
#
# NOTES: 
#	It is advised that all username, password, category and localFolder options are given.
#	This is done to improve efficiency, as the already existing tiles are not re-downloaded to 
#	saving disk space and server resources. 
#
#	Stitching is done using gdal_translate.py
#
# LICENSE:
#	This shell script automates the ASTER downloading procedure. It downloads the ASTER dem 
# server (www.gdem.aster.ersdac.or.jp), using the given username, password, and category. 
#
#	ASTER-GDEM distribution policy requires collection of such information for statistical
# purposes. This script is "AS-IS" software. The author is not responsible for any technical or
# legal problems the users may face.  This script was developed in January 2011. If it is still running
# it is because the METI officials have not taken steps to limit use of this script.
#	
#	For more information type construct_aster_dem.sh license
#
# Author:
#   Batuhan Osmanoglu, RSMAS-MGG, University of Miami, 2011
#   Beta-Tester: Heresh Fattahi, RSMAS-MGG, University of Miami, 2011
#   Parts of this script is taken from construct_dem.sh, Freek van Leijen, Zbigniew Perski, 
#     Mahmut Arikan and Petar Marinkovich, TU-DELFT, DORIS package.
#   Thanks to Mahmut Arikan and Petar Marinkovich for providing information on stitching Aster tiles.
#   
# ChangeLog:
#   Initial version: 1.0, 2011 01 10

printLicense(){
cat << _ENDLICENSE_
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESSED OR IMPLIED, INCLUDING, 
BUT NOT LIMITED TO, WARRANTIES OF QUALITY, PERFORMANCE, NON-INFRINGEMENT, MERCHANTABILITY, OR 
FITNESS FOR A PARTICULAR PURPOSE.  FURTHER, THE AUTHOR DOES NOT WARRANT THAT THE SOFTWARE OR ANY
RELATED SERVICE WILL ALWAYS BE AVAILABLE.

YOU ASSUME ALL RISK ASSOCIATED WITH THE INSTALLATION AND USE OF THE SOFTWARE. IN NO EVENT SHALL 
THE AUTHORS LIABLE FOR CLAIMS, DAMAGES OR OTHER LIABILITY ARISING FROM, OUT OF, OR IN CONNECTION 
WITH THE SOFTWARE. LICENSE HOLDERS ARE SOLELY RESPONSIBLE FOR DETERMINING THE APPROPRIATENESS OF 
USE AND ASSUME ALL RISKS ASSOCIATED WITH ITS USE, INCLUDING BUT NOT LIMITED TO THE RISKS OF 
PROGRAM ERRORS, DAMAGE TO EQUIPMENT, LOSS OF DATA OR SOFTWARE PROGRAMS, OR UNAVAILABILITY OR 
INTERRUPTION OF OPERATIONS.

ASTER Data Policies
ASTER Redistribution Policies for the General Public
ASTER Global DEM (GDEM) data are subject to redistribution and citation policies. Before ordering 
ASTER GDEM data, users must agree to redistribute data products only to individuals within their 
organizations or projects of intended use, or in response to disasters in support of the GEO 
Disaster Theme. When presenting or publishing ASTER GDEM data, users are required to include a 
citation stating, "ASTER GDEM is a product of METI and NASA."

Because there are known inaccuracies and artifacts in the data set, please use the product with 
awareness of its limitations. The data are provided "as is" and neither NASA nor METI/ERSDAC will 
be responsible for any damages resulting from use of the data.

For more information: https://lpdaac.usgs.gov/lpdaac/products/aster_policies
_ENDLICENSE_
exit 0;
}

function abs(){
 echo "${1}" | tr -d "-"
}

function canonicalPath(){
  #from http://snipplr.com/view/18026/canonical-absolute-path/
  echo $(cd $(dirname $1); pwd -P)/$(basename $1)
}

function ceil() {
  local float_in ceil_val
  float_in=${1}
  ceil_val=${float_in/.*}
  if [[ "${float_in}" == *.* ]]; then    
    ceil_val=$((ceil_val+1))
  fi
  echo ${ceil_val}
}
    
function checkLocalFolder(){
#returns empty string if can not find. Otherwise return full path.
  fullPath=`canonicalPath ${1}`
  if [ -e ${fullPath} ]; then
    echo ${fullPath}
  fi
}

function cleanup(){
#cleanup temporary files
for file in $@
do
  rm -rf ${file} #be silent, no need for error messages.
done
}

function floor() {
#set -x
  local float_in decimal floor_val
  float_in=${1}
#  if [[ "${float_in}" == *.* ]] && echo  || echo "veli"
  decimal=${float_in##*.}
  floor_val=${float_in/.*}
  echo ${floor_val}
#echo ${1%%.*}  | ${AWK} '{ if ($1 < 0) $1 = $1 - 1; print $1 }'
#set +x
}

getTile(){
  if [[ ${loggedIn} == false ]]; then
    logMeIn
    [[ $? -eq 126 ]] && echo "Can not login." && return 126
  fi
  tileStr=`echo ${1} ${2} | awk '{printf "%0.2d_%0.3d", $2+25,-$1+82}'`
  echo "Downloading Tile: ${tileStr}"
  timeNow=`date +%s%N | cut -c 1-13`
  wget -nv --load-cookies ${cookieFile} -O ${selectFile} --header "content-type:application/x-www-form-urlencoded" --post-data "_gd_tiles=${tileStr}," "http://www.gdem.aster.ersdac.or.jp/gdServletAsyn/SetTileList?time=${timeNow}"
  wget -nv --load-cookies ${cookieFile} -O ${listFile} --header "content-type:application/x-www-form-urlencoded" --post-data "_gd_tiles=${tileStr}," "http://www.gdem.aster.ersdac.or.jp/gdServlet/SelectTile"
  wget -nv --load-cookies ${cookieFile} -O ${categoryFile} --post-data "_gd_tiles=${tileStr}," "http://www.gdem.aster.ersdac.or.jp/gdServlet/StartLogin"
  wget -nv --load-cookies ${cookieFile} -O ${downloadsFile}  "http://www.gdem.aster.ersdac.or.jp/gdServlet/StartDownload?_gd_purpose_category=${c}"
  downloadSite=`grep download_immediate_site ${downloadsFile} | cut -d">" -f2 |cut -d"<" -f1`
  fileName=`grep _gd_download_file_name ${downloadsFile} | cut -d'"' -f6`
  echo ${downloadSite}${fileName}
  wget --load-cookies ${cookieFile} -O${tmpFolder}/${fileName} --post-data "_gd_download_file_name=${fileName}" "${downloadSite}gdServlet/Download"
  unzip -j -d ${f} ${tmpFolder}/${fileName}
  if [[ $? -ne 0 ]]; then
    echo "Error downloading tile. Non-existing tile. Might be all water."
    return 125 # 125- Missing Tile
    #downloadSite=`grep download_back_log_site ${downloadsFile} | cut -d">" -f2 |cut -d"<" -f1`
    #wget --load-cookies ${cookieFile} -O${tmpFolder}/${fileName} --post-data "_gd_download_file_name=${fileName}" "${downloadSite}gdServlet/Download"
    #unzip -j -d ${f} ${tmpFolder}/${fileName}
    #[[ $? -ne 0 ]] && echo "Got an error again. See ${tmpFolder}/${fileName}" && exit 125
  fi
  rm ${tmpFolder}/${fileName}
  return 0
}

logMeIn(){
  if [ "${u:-isEmpty}" == isEmpty ] || [ "${p:-isEmpty}" == isEmpty ] || [ "${c:-isEmpty}" == isEmpty ]; then 
    echo "Missing login information."
    return 126 #126-can not login    
  else
    echo "Logging in user: ${u}"  
    wget -nv --save-cookies ${cookieFile} --keep-session-cookies --post-data "_gd_register_user_name=${u}&_gd_register_password=${p}" -O ${loginFile} "http://www.gdem.aster.ersdac.or.jp/gdServlet/Login"
    userName=`grep loggedin_info_value ${loginFile} | cut -d">" -f2 | cut -d"<" -f1`
    if [ $? -ne 0 ] || [ "${userName}" != "${u}" ]; then
      echo "Login Error!"
      echo "   Can not login as ${u}"
      return 126 #126 can not login
    else
      loggedIn=true
    fi
  fi
  return 0
}

logMeOut(){
  echo "Logging out user: ${u}"
  wget -nv --load-cookies ${cookieFile} -O ${logoutFile} "http://www.gdem.aster.ersdac.or.jp/gdServlet/Logout"
  return $?
}

if [ "${1:-allEmpty}" == "allEmpty" ]; then
  sed -n -e '/^# USAGE:/,/^$/ s/^# \?//p' < ${0}
  exit 0
elif [ "${1}" == "license" ]; then
  printLicense
fi

#initial setup
AWK=`AWK=$(which nawk 2> /dev/null); [ "$AWK" == "" ] && echo $(which awk) || echo $AWK` # MA awk variable: 1. look for nawk (on old systems) else 
tmpFolder="/tmp"
loginFile="${tmpFolder}/loginFile"
logoutFile="${tmpFolder}/logoutFile"
cookieFile="${tmpFolder}/cookieFile"
selectFile="${tmpFolder}/selectFile"
listFile="${tmpFolder}/listFile"
categoryFile="${tmpFolder}/categoryFile"
downloadsFile="${tmpFolder}/downloadsFile"
demListFile="${tmpFolder}/demListFile"
temporaryFiles=(${loginFile} ${logoutFile} ${cookieFile} ${selectFile} ${listFile} ${categoryFile} ${downloadsFile} ${demListFile})
loggedIn=false

#cleanup temporary files from last run
cleanup ${temporaryFiles[@]}

#get options and assign them as $n=projectName etc.
while getopts "n:u:p:c:f:s:" flag
do
  eval export ${flag}=${OPTARG}
done
#check input flags
[[ "${n:-isEmpty}" == "isEmpty" ]] && n="dem" && echo "Project name set to dem"
#[[ "${u:-isEmpty}" == "isEmpty" ]] && echo "Username is not given."
#[[ "${p:-isEmpty}" == "isEmpty" ]] && echo "Password is not given."
[[ "${c:-isEmpty}" != "isEmpty" ]] && c=`echo ${c} |sed 's/\<./\u&/'` && echo "Category set to ${c}"
[[ "${f:-isEmpty}" == "isEmpty" ]] && f="./" && echo "Local folder is set to ./"
[[ "${s:-isEmpty}" == "isEmpty" ]] && s="0" && echo "Downloaded tiles will not be stitched together."

# get W E S N
for ((k=1; k<$OPTIND; k++ ))
do
  shift
done  
unset flag OPTARG OPTIND  
W=`floor ${1}`
E=`ceil ${2}`
S=`floor ${3}`
N=`ceil ${4}`
echo "Coordinates(WESN)= ${W} ${E} ${S} ${N}"
#check coordinates
[[ "${N:-isEmpty}" == "isEmpty" ]] && echo "Please enter four corner coordinates." && exit 127
[ "${W}" -gt "${E}" ] && echo -e "\n E:${E} can't be less than W:${W}! \n" && exit 127
[ "${S}" -gt "${N}" ] && echo -e "\n N:$N can't be less than S:$S! \n" && exit 127 

echo ""
echo "--------------------------------------------------"
echo "Downloading gdem and merging the tiles ..."
echo "--------------------------------------------------"
echo ""
###################################################3333
#exit
#######################################################
countLat=1
for ((lat=${S}; lat <= ${N}; lat++))
do
  if [ "${lat}" -gt 0 ]; then
    latL="N" 
  else
    latL="S" #latL= lat letter
  fi
  latA=`abs "${lat}"` # latA= lat Absolute
  countLon=1
  for ((lon=${W}; lon <= ${E}; lon++))
  do
    if [ "${lon}" -gt 0 ]; then
      lonL="E" 
    else
      lonL="W"
    fi
    lonA=`abs "${lon}"` #lonA= lon Absolute
    lonF=`printf "%0.3d" ${lonA}` #lonF = lon Formatted
    tileFileName="ASTGTM_${latL}${latA}${lonL}${lonF}_dem.tif"
    echo ${tileFileName}
    filePath=`checkLocalFolder "${f}/${tileFileName}"`
    if [ "${filePath:-isEmpty}" == "isEmpty" ]; then       
      echo "Downloading ASTGTM_${latL}${lat}${lonL}${lonF}.zip"
      getTile ${lat} ${lon}
      if [[ $? -ne 0 ]]; then
        echo "Skipping ASTGTM_${latL}${lat}${lonL}${lonF}"
      else
        echo "${f}/${tileFileName}" >> ${demListFile}
      fi
    else
      echo "File exists. ${filePath}"
      echo "${f}/${tileFileName}" >> ${demListFile}
    fi 
  done
done  

[[ ${loggedIn} == true ]] && logMeOut


# merging tiles using gdal
case ${s} in
  1)
    #method1: Thanks to Mahmut Arikan @ TU-DELFT
    gdalbuildvrt ${n}.vrt -input_file_list ${demListFile}
    #gdal_translate ${n}.vrt -outsize 10% 10% -ot Int16 -of Gtiff -co "TFW=YES" ${n}.tif #will also create ${n}.tfw
    gdal_translate ${n}.vrt -ot Int16 -of ENVI ${n}.dem #will also create ${n}.hdr 
  ;;
  2)
    #method2: Thanks to Petar Marinkovich 
    gdal_merge.py -n -32768 -o ${n} -of mff2 -v --optfile ${demListFile}
  ;;
  3)
    #method3: Thanks to Petar Marinkovich 
    gdal_merge.py -n -32768 -of GTiff -co "TFW=YES" -v -o ${n}.tif --optfile ${demListFile}  
  ;;
  *)
    #no stitching.
    echo "Stitching method was given as ${s}. Stitching is only done for methods 1 and 2."
  ;;
esac
#cleanup temporary files
cleanup ${temporaryFiles[@]}
