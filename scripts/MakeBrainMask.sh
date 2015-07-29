#!/bin/bash
## \author Hans J. Johnson & Regina Kim
## Test to register mini-pig-whole-brain to new mini-pig

export NSLOTS=2
export NAMICBUILD=/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_OSX_201505/
export BINDIR=$NAMICBUILD/bin
export PATH=$BINDIR:$NAMICBUILD/SimpleITK-build/lib:$PATH
export PYTHONPATH=$NAMICBUILD/SimpleITK-build/Wrapping/:$NAMICBUILD/BRAINSTools/AutoWorkup/:$NAMICBUILD/NIPYPE:$PYTHONPATH
#wfrun="SGEGraph"

#SUBJECTID=M340P100
#SESSIONID=M340P100_20131031
SUBJECTID=$1
SESSIONID=$2
#OUT_DIR=/Shared/johnsonhj/HDNI/20150416_MiniPigData/RegistrationTesting/${SESSIONID}
OUT_DIR=~/Desktop/MiniPig/${SESSIONID}

WARPEDLBLLIST=""
WARPEDT1LIST=""
for ATLAS_NUM in 1 2; do

if [ ${ATLAS_NUM} -eq 1 ] ;then
  ATLAS_SUBJECT=M268P100
  ATLAS_SESSION=M268P100_20130606
else
  ATLAS_SUBJECT=M340P100
  ATLAS_SESSION=M340P100_20131031
fi
MOVING_MINIPIG=/Shared/johnsonhj/HDNI/20150416_MiniPigData/${ATLAS_SUBJECT}/${ATLAS_SESSION}/${ATLAS_SESSION}_3DT1TFEhrs.nii.gz
MOVING_MINIPIG_MASK=/Shared/johnsonhj/HDNI/20150416_MiniPigData/${ATLAS_SUBJECT}/${ATLAS_SESSION}/${ATLAS_SESSION}_whole_brain_mask.nii.gz

echo "PROCESSING: ${ATLAS_SESSION}"

FIXED_MINIPIG=/Shared/johnsonhj/HDNI/20150416_MiniPigData/${SUBJECTID}/${SESSIONID}/${SESSIONID}_3DT1TFEhrs.nii.gz
#FOLLOWING MASK WAS NOT USED IN THE SCRIPT
#FIXED_MINIPIG_OUTPUT_MASK=$OUT_DIR/${SUBJECTID}/${SESSIONID}/${SESSIONID}_whole_brain_mask.nii.gz


mkdir -p ${OUT_DIR}
cd ${OUT_DIR}

INPUT_ANTS_TRANSFORM=/Shared/johnsonhj/HDNI/20150416_MiniPigData/RegistrationTesting/${SESSIONID}/${ATLAS_SESSION}2${SESSIONID}_tfmComposite.h5
if [ ! -f ${INPUT_ANTS_TRANSFORM} ]; then
echo "MISSING: ${INPUT_ANTS_TRANSFORM}"
exit -1
${BINDIR}/antsRegistration \
  --verbose \
  --collapse-output-transforms 0 \
  --dimensionality 3 \
  --float 1 \
  --initialize-transforms-per-stage 1 \
  --interpolation Linear \
  --output [ ${ATLAS_SESSION}2${SESSIONID}_tfm, ${ATLAS_SESSION}2${SESSIONID}.nii.gz, ${SESSIONID}2${ATLAS_SESSION}.nii.gz ] \
  --save-state ${SESSIONID}SavedBeginANTSSyNState.h5 \
  --transform Affine[ 0.1 ] \
  --metric MI[ ${FIXED_MINIPIG}, ${MOVING_MINIPIG}, 1, 32, Regular, 0.27 ] \
  --convergence [ 1000x1000, 5e-08, 10 ] \
  --smoothing-sigmas 3.0x2.0vox \
  --shrink-factors 8x4 \
  --use-estimate-learning-rate-once 0 \
  --use-histogram-matching 1 \
  --transform SyN[ 0.1, 3.0, 0.0 ] \
  --metric CC[ ${FIXED_MINIPIG}, ${MOVING_MINIPIG}, 1, 3, None, 0.8 ] \
  --convergence [ 1000x250, 5e-07, 10 ] \
  --smoothing-sigmas 3.0x2.0vox \
  --shrink-factors 8x4 \
  --use-estimate-learning-rate-once 0 \
  --use-histogram-matching 1 \
  --winsorize-image-intensities [ 0.01, 0.99 ]  \
  --write-composite-transform 1

fi

SUBJECT_BRAIN_MASK=/Shared/johnsonhj/HDNI/20150416_MiniPigData/RegistrationTesting/${SESSIONID}/${SESSIONID}_stage1_${ATLAS_SESSION}_brain_mask.nii.gz
if [ ! -f ${SUBJECT_BRAIN_MASK} ]; then
${BINDIR}/BRAINSResample \
    --interpolationMode Linear \
    --pixelType binary \
    --referenceVolume ${FIXED_MINIPIG} \
    --inputVolume ${MOVING_MINIPIG_MASK} \
    --warpTransform ${ATLAS_SESSION}2${SESSIONID}_tfmComposite.h5  \
    --outputVolume ${SUBJECT_BRAIN_MASK}
fi
WARPED_T1_IMAGE=/Shared/johnsonhj/HDNI/20150416_MiniPigData/RegistrationTesting/${SESSIONID}/${SESSIONID}_T1_${ATLAS_SESSION}_warped_atlas.nii.gz
if [ ! -f ${WARPED_T1_IMAGE} ]; then
${BINDIR}/BRAINSResample \
    --interpolationMode Linear \
    --pixelType short \
    --referenceVolume ${FIXED_MINIPIG} \
    --inputVolume ${MOVING_MINIPIG} \
    --warpTransform ${ATLAS_SESSION}2${SESSIONID}_tfmComposite.h5  \
    --outputVolume ${WARPED_T1_IMAGE}
fi

if [ ${ATLAS_NUM} -eq 1 ]; then
WARPEDLBLLIST="${SUBJECT_BRAIN_MASK}"
WARPEDT1LIST="${WARPED_T1_IMAGE}"
ORIG_IMAGES="${FIXED_MINIPIG}"
else
WARPEDLBLLIST="${WARPEDLBLLIST} ${SUBJECT_BRAIN_MASK}"
WARPEDT1LIST="${WARPEDT1LIST} ${WARPED_T1_IMAGE}"
ORIG_IMAGES="${ORIG_IMAGES} ${FIXED_MINIPIG}"
fi

echo "DONE: ${SUBJECT_BRAIN_MASK}"
done

OUTPUT_BRAINMASK=$OUT_DIR/${SESSIONID}_malf_brainmask.nii.gz
if [ ! -f ${OUTPUT_BRAINMASK} ]; then
  ${BINDIR}/jointfusion 3 1 \
     -g ${WARPEDT1LIST} \
    -tg ${ORIG_IMAGES} \
    -l ${WARPEDLBLLIST} \
    -m Joint[0.1,2] \
    ${OUTPUT_BRAINMASK}
fi

#T1_fn   =     sys.argv[1] #'/Shared/johnsonhj/HDNI/20150416_MiniPigData/M340P100/M340P100_20131031/M340P100_20131031_3DT1TFEhrs.nii.gz'
#T1_amira_fn=  sys.argv[2] #'/Shared/johnsonhj/HDNI/20150416_MiniPigData/M340P100/M340P100_20131031/M340P100_20131031_3DT1TFEhrs_amira.nii.gz'
#amira_fn=     sys.argv[3] #'/Shared/johnsonhj/HDNI/20150416_MiniPigData/M340P100/M340P100_20131031/M340P100_20131031_amira_labels.nii.gz'
#malf_brain_fn=sys.argv[4] #'/Shared/johnsonhj/HDNI/20150416_MiniPigData/RegistrationTesting/M340P100_20131031/M340P100_20131031_malf_brainmask.nii.gz'
#output = sys.argv[5]

FIXED_MINIPIG_AMIRA=/Shared/johnsonhj/HDNI/20150416_MiniPigData/${SUBJECTID}/${SESSIONID}/${SESSIONID}_3DT1TFEhrs_amira.nii.gz
FIXED_MINIPIG_AMIRA_BRAIN=/Shared/johnsonhj/HDNI/20150416_MiniPigData/${SUBJECTID}/${SESSIONID}/${SESSIONID}_amira_labels.nii.gz

OUTPUT_AUTO_BRAIN_LABEL=$OUT_DIR/${SESSIONID}_amira_brain_label.nii.gz
if [ ! -f ${OUTPUT_AUTO_BRAIN_LABEL} ]; then
  echo "python /Shared/johnsonhj/HDNI/20150416_MiniPigData/RegistrationTesting/MergeAmiraMALFLabels.py \
     ${FIXED_MINIPIG} \
     ${FIXED_MINIPIG_AMIRA} \
     ${FIXED_MINIPIG_AMIRA_BRAIN} \
     ${OUTPUT_BRAINMASK} \
     ${OUTPUT_AUTO_BRAIN_LABEL}"
  python /Shared/johnsonhj/HDNI/20150416_MiniPigData/RegistrationTesting/MergeAmiraMALFLabels.py \
     ${FIXED_MINIPIG} \
     ${FIXED_MINIPIG_AMIRA} \
     ${FIXED_MINIPIG_AMIRA_BRAIN} \
     ${OUTPUT_BRAINMASK} \
     ${OUTPUT_AUTO_BRAIN_LABEL}
fi

echo "DONE: lsl ${OUTPUT_BRAINMASK} ${FIXED_MINIPIG}"
exit $?


