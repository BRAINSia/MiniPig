#!/bin/bash - 
#===============================================================================
#
#          FILE: splitGoettingenAtlas.sh
# 
#         USAGE: ./splitGoettingenAtlas.sh 
# 
#   DESCRIPTION: 
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

set -o nounset                              # Treat unset variables as an error

. source_fsl

ATLAS=$(basename $1)
SDIR=$(dirname $1)
DDIR=$SDIR/sliced_$(basename $ATLAS .nii.gz)

mkdir $DDIR

for i in $(seq 0 251); do
  fslmaths $SDIR/$ATLAS -sub $i -thr 0 -uthr 1 $DDIR/"$i"_$ATLAS
done

