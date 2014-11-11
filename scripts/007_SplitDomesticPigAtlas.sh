#!/bin/bash - 
#===============================================================================
#
#          FILE: SplitGoettingenAtlas.sh
# 
#         USAGE: ./SplitDomesticPigAtlas.sh 
# 
#   DESCRIPTION: Creates a binary mask for every region contained in the
#                atlas. Masks are used as template to create the complement
#                based on the MiniPig atlas.
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Robin Schubert (RS), robin.schubert@ghi-muenster.de
#  ORGANIZATION: GHI
#       CREATED: 09/05/2014 14:16
#      REVISION:  ---
#===============================================================================

# . source_fsl

ATLAS=$(basename $1)
SDIR=$(dirname $1)
DDIR=$SDIR/sliced_$(basename $ATLAS .nii.gz)

mkdir $DDIR

for i in $(seq 0 251); do
  fslmaths $SDIR/$ATLAS -sub $i -thr 0 -uthr 1 $DDIR/"$i"_$ATLAS
done

