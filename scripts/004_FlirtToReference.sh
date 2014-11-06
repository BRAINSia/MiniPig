#!/bin/bash - 
#===============================================================================
#
#          FILE: 004_FlirtToReference.sh
# 
#         USAGE: ./004_FlirtToReference.sh <File> <OutDir> [Reference]
# 
#   DESCRIPTION: Used to flirt a single brain to a standard reference
#                with a 12 degree of freedoms (affine) transformation
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Robin Schubert (RS), robin.schubert@ghi-muenster.de
#  ORGANIZATION: GHI
#       CREATED: 09/03/2014 13:36
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

. source_fsl

if [ -z $2 ]; then
    echo "usage: $0 <File> <OutDir> [Reference]"

# set reference brain if specified
if [ -z $3 ]; then  
  REFERENCE="" # to be customized
else 
  REFERENCE=$3
fi

SDIR=$(dirname $1)
SFILE=$(basename $1)
ODIR=$3
OUTFILE="fl$SFILE"
MATFILE="$(basename $SFILE .nii.gz).mat"

flirt -in $SDIR/$SFILE -ref $REFERENCE -out $ODIR/$OUTFILE -omat $ODIR/$MATFILE -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear

# echo output file and matfile for usage in pipe
echo $OUTFILE $MATFILE
