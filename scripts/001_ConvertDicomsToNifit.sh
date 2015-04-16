#!/bin/bash - 
#===============================================================================
#
#          FILE: 001_ConvertDicomsToNifti.sh
# 
#         USAGE: ./001_ConvertDicomsToNifti.sh <SDIR> <DDIR>
# 
#   DESCRIPTION: The source directory (SDIR) must contain a DICOM directory
#                that is converted into .nii.gz format
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Robin Schubert (RS), robin.schubert@ghi-muenster.de
#  ORGANIZATION: GHI
#       CREATED: 08/01/2014 13:43
#      REVISION:  ---
#===============================================================================


#
# Converts dicom Files to nii.gz
#
# @Params: Source Directory, Destination Directory
#

if [ -z $2 ]; then
    echo 'usage: $0 <SDIR> <DDIR>'
    exit 0
fi

SDIR=$1
DDIR=$2

# creating destintion directory if not existing
mkdir $DDIR
mkdir $DDIR/tmp

# converting file
dcm2nii -4 Y -a N -c Y -d Y -e N -f N -g Y -i Y -m N -n Y -o $DDIR/tmp -p Y -r N -s N -v Y -x N $SDIR/DICOM
# reorienting file
FILENAME=$(basename $(ls $DDIR/tmp/*.nii.gz) ".nii.gz" )
mv $DDIR/tmp/*.nii.gz $DDIR/"$FILENAME".nii.gz
mv $DDIR/tmp/*.bval $DDIR/"$FILENAME".bval
mv $DDIR/tmp/*.bvec $DDIR/"$FILENAME".bvec

# cleaning up
rm -r $DDIR/tmp/

# return resulting filename for usage in pipe
echo $DDIR/"$FILENAME".nii.gz
