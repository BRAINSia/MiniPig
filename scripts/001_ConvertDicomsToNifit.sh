#!/bin/bash
# \author Robin S.

# We first converted the DICOMs to nifti format using dcm2nifti.
# To ensure consistend orientation, every image was reoriented with fslreorient2std,
# although due to the pig's positions, this is not 'real' standard space.

# widh SDIR = SourceDirectory and DDIR = DestinationDirectory
# the -4 option and reorientating is included, since we use the
# same script for other sequences, e.g. DTI sequences, that have
# different orientations.
for i in $FILES; do
  mkdir $DDIR/tmp
  echo "processing file: $i"
  dcm2nii -4 Y -a N -c Y -d N -e N -f Y -g Y -i N -m N -n Y -o $DDIR/tmp -p N -r N -s N -v Y -x N $SDIR/$i/DICOM
  echo "reorienting $i"
  fslreorient2std $DDIR/tmp/IM*.nii.gz $DDIR/$i.nii.gz
  mv $DDIR/tmp/*.bval $DDIR/$i.bval
  mv $DDIR/tmp/*.bvec $DDIR/$i.bvec
  echo "cleaning up"
  rm -r $DDIR/tmp/
done
