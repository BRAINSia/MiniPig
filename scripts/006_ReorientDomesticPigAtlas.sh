#!/bin/bash - 
#===============================================================================
#
#          FILE: reorientGoettingen.sh
# 
#         USAGE: ./reorientGoettingen.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Robin Schubert (RS), robin.schubert@ghi-muenster.de
#  ORGANIZATION: GHI
#       CREATED: 09/05/2014 13:24
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

. source_fsl

ATLAS=$1

fslorient -deleteorient $ATLAS

fslswapdim $ATLAS x -z -x $ATLAS

fslorient -setqformcode 1 $ATLAS
fslorient -setsformcode 1 $ATLAS

fslswapdim $ATLAS RL PA IS $ATLAS
