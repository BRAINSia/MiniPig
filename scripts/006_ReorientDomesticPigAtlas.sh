#!/bin/bash - 
#===============================================================================
#
#          FILE: 006_ReorientDomesticPigAtlas.sh
# 
#         USAGE: ./006_ReorientDomesticPigAtlas.sh <AtlasFile> (nii.gz)
# 
#   DESCRIPTION: Reorients the freely available domestic pig atlas to
#                the same orientation as the minipigs. The minipigs
#                orientation is not 'standard' since they are in
#                sphinx position when scanning. 
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

if [ -z $1]; then
    echo "usage: $0 <AtlasFile>"
    exit 0
fi

# TODO make fsl commands available in shell
. source_fsl

ATLAS=$1

# deleting existing orientation
fslorient -deleteorient $ATLAS

# swapping axes
fslswapdim $ATLAS x -z -x $ATLAS

# enabling q and sform
fslorient -setqformcode 1 $ATLAS
fslorient -setsformcode 1 $ATLAS

# swapping orientation, finalize
fslswapdim $ATLAS RL PA IS $ATLAS
