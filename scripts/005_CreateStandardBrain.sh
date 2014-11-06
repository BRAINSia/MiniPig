#!/bin/bash - 
#===============================================================================
#
#          FILE: pipeRawTemplate.sh
# 
#         USAGE: ./pipeRawTemplate.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Robin Schubert (RS), robin.schubert@ghi-muenster.de
#  ORGANIZATION: GHI
#       CREATED: 09/01/2014 16:40
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

# TODO
. source_fsl

SDIR=$1
ODIR=$2

if [ -z $2]; then
    echo "usage: $0 <InputDir> <OutputDir> [Whitelist]"
    exit 0
fi

BRAINS=""
COUNT=0

for i in $(ls $SDIR)
do
    # cropping converted raw
    FILE=$(bash 002_CropToBrainRegion.sh $SDIR/$i $ODIR)
    # extracting brain, collecting Filenames
    BRAINS="$BRAINS $(bash 003_ExtractBrain.sh $FILE $ODIR)"
    COUNT=$(($COUNT + 1))
done

# refine list of brains if WHITELIST is specified
if [ -n $3 ]; then
    WHITELIST="$3"
    OLDBRAINS="$BRAINS"
    BRAINS=""
    COUNT=0
    for i in $OLDBRAINS; do
        FILE=$(cat $WHITELIST | grep $i)
        BRAINS="$BRAINS $FILE"
        COUNT=$(($COUNT + 1))
    done
fi

echo $COUNT
echo $FILES
flirt_average $COUNT $BRAINS $SDIR/fine_average_brain.nii.gz -omat $SDIR/fine_average_brain.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear


#
# flirt brain images to template, generating mat files
# -> potentially useless
#
FILES=$(ls $SDIR | grep ^exc)

for i in $FILES; do
  echo "processing $i"
  bash flirtSingle.sh $SDIR/$i $SDIR 
done


