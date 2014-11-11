#!/bin/bash - 
#===============================================================================
#
#          FILE: 003_extractSingleBrain.sh
# 
#         USAGE: ./003_extractSingleBrain.sh <File> <OutputDir> 
# 
#   DESCRIPTION: brain extraction using fsl bet with -R option (iterative)
#                fracint=0.4 still exploratory tends to leave more
#                non-brain tissue rather than to remove brain tissue
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

set -o nounset                              # Treat unset variables as an error

#
#
FILE=$(basename $1)
SDIR=$(dirname $1)
DDIR=$2

FRACINT=0.4
GRADIENT=0

bet $SDIR/$FILE $DDIR/ex$FILE -f $FRACINT -g $GRADIENT -R

#return resulting filename for usage in pipe
echo $DDIR/x$FILE
