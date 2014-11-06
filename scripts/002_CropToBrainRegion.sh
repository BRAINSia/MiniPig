#!/bin/bash - 
#===============================================================================
#
#          FILE: 002_CropToBrainRegion.sh
# 
#         USAGE: ./002_CropToBrainRegion.sh <FILE> <DDIR>
# 
#   DESCRIPTION: crops given FILE with fslroi, using AC coordinates specified
#                in $CROPDATA file. The width of x, y and z are set fixed from
#                empiric data.
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

# check for unset but required args
if [ -z $2 ]; then
    echo "usage: $0 <FILE> <DDIR> [WHITELIST]"
    exit 0
fi

FILE=$(basename $1)
SDIR=$(dirname $1)
DDIR=$2

# optional arg: whitelist with coordinates of anterrior commissure
# default file used if left empty
if [ -n $3]; then
    CROPDATA="$3"
else
    CROPDATA="/var/mri/fractional_anisotropy/txt/anterior_commissure_whitelist_2014-06-13.txt"
fi

# the resulting brain-only image size was chosen so that larger brains
# would fit too
X_CROP=180
Y_CROP=130
Z_CROP=190

# reading from AC list with $1 = filename and $2-$4 = x, y, z
# TODO if consisten renaming is introduced, list has to be updated
while read line; do
  set -- $line
  if [ $1 == $(basename $FILE .nii.gz) ]; then
    #adding pixelshift of 23px in x direction
    X_START=$(echo "($2 - ($X_CROP/2) + 23)" | bc)
    Y_START=$(echo "($3 - ($Y_CROP/2))" | bc)
    Z_START=$(echo "($4 - ($Z_CROP/2))" | bc)

    fslroi $SDIR/$FILE $DDIR/c$FILE $X_START $X_CROP $Y_START $Y_CROP $Z_START $Z_CROP 
  fi
done < $CROPDATA

# returning resulting filename for usage in pipelines
echo $DDIR/c$FILE
