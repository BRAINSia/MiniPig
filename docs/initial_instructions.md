#Minipig brain processing

Here is a collection of bash scripts I have written and used so far. I've tried to make it as clear as possible with some extra comments. But I guess that the exact code might not even be of much interest to you, you can get the essence by skimming over it.

## Overview

In general the way we went was

1. We first converted the DICOMs to nifti format using dcm2nifti. To ensure consistend orientation, every image was reoriented with fslreorient2std, although due to the pig's positions, this is not 'real' standard space.

2. We viewed every T13D image with fslviewer and looked up the anterrior comissure, the coordinates were saved into a textfile.

3. Then we saved cropped copies of the T13D images containing only the brain region, using the AC coordinates and fslroi

4. We're lucky that brain extraction works pretty good with our images, using fsl bet. For our template I've used a fractional intensity value of 0.4 and a gradient of 0, also using the multiple iteration option -R. This tends to leave more non-brain tissue in the image, rather than to delete brain tissue.
We also decided to cut away the olfactory bulb, which has a very nested structure and is imho almost impossible to separate. Luckily bet cuts that bulb away out of the box ;)

5. To create a standard brain I used fsl flirt_average (affine transformations). The result was already pretty good, but I tried to improve it by flirting every image separately on the new coarse standard brain, saving the transformation matrix and then again applying it in a linear transformation with the template as reference. The mean of the resulting transformated brains was supposed to be the fine standard template, but actually I couldn't observe any improvement by doing this, though I didn't test with mathematical means, just compared them by looking at them.
I've clipped the standard brain intensity at reasonable values (I think 250 - 1000 or so) to remove small outlying parts, and the overexposed pituitary gland.
*(non-linear transformation were not possible on the extracted images because of the left-overs of non-brain tissue and the variation in the extractions. I've tried it with the non-exctracted brains, but the result was pretty poor, I didn't even save it.)*

6. The step of obtaining an atlas (or few parts of an atlas) maybe was the unconventional one. There is a very pretty atlas of the domestic pic freely available (<https://www6.rennes.inra.fr/adnc_eng/Research/Research-Highlights/Pig-brain-atlas>) that I matched on our standard brain with fsl flirt, which actually worked surprisingly well. Then I separated the atlas into the single masks and loaded them into fslview, together with our standard template. I've started to manually draw the functional regions of the basal ganglia on new masks, using the transformed domestic pig masks as guidelines.
As a physicist I'm not that much of an expert in brain anatomy, but I did the best I could in short time ;)

## Code snippets

### converting and reorienting
``` sh
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
```

### cropping around the AC
``` sh
# file containing the AC coordinates
CROPDATA="/var/mri/fractional_anisotropy/txt/anterior_commissure_whitelist_2014-06-13.txt"

# the resulting brain-only image size was chosen so that larger brains would fit too.
X_CROP=180
Y_CROP=130
Z_CROP=190

# reading from CROPDATA file to process the images. Somehow we got a pixelshift
# between the captured coordinates of the AC in x-direction that we cannot 
# explain. The quickest fix was to add 23 pixels.
while read line; do
  set -- $line
  if [ $1 == $(basename $FILE .nii.gz) ]; then
    # adding pixelshift of 23px in x direction
    X_START=$(echo "($2 - ($X_CROP/2) + 23)" | bc)
    Y_START=$(echo "($3 - ($Y_CROP/2))" | bc)
    Z_START=$(echo "($4 - ($Z_CROP/2))" | bc)

    fslroi $SDIR/$FILE $DDIR/c$FILE $X_START $X_CROP $Y_START $Y_CROP $Z_START $Z_CROP 
  fi
done < $CROPDATA
```
### extract the brain with bet
``` sh
FRACINT=0.4
GRADIENT=0

bet $SDIR/$FILE $DDIR/ex$FILE -f $FRACINT -g $GRADIENT -R
```

### creating the standard brain
``` sh
# create raw template with flirt_average
#
# WHITELIST contains only those brains that did not suffer from eye movement
# or other artifacts during acquisition
WHITELIST="/var/mri/fractional_anisotropy/txt/flirt_average_whitelist_2014-09-01.txt"

FILES=""
COUNT=0
while read line
do
  set -- $line
  FILE=$(ls $SDIR | grep flflexc$line)
  if [ ! $FILE == "" ]; then
    FILES="$FILES $SDIR/$FILE"
    COUNT=$(($COUNT + 1)) 
  fi
done < $WHITELIST

echo $COUNT
echo $FILES
flirt_average $COUNT $FILES $SDIR/fine_average_brain.nii.gz -omat $SDIR/fine_average_brain.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear

#
# flirt brain images to template, generating mat files
#

FILES=$(ls $SDIR | grep ^exc)

for i in $FILES; do
  echo "processing $i"
  bash flirtSingle.sh $SDIR/$i
done


#
# flirt head images with mat files to template
#

FILES=$(ls $SDIR | grep ^c[0-9].*\.nii.gz)
MATFILES=$(ls $SDIR | grep ^exc.*\.mat)
REFERENCE="/var/mri/fractional_anisotropy/tmp/ehdn_t13d_converted/001_average_brain.nii.gz"

for i in $MATFILES; do
  # find file matching the start of mat file without "ex"
  FILE=$(ls $SDIR | grep ^${i:2:8})
  echo "processing $FILE"
  flirt -in $SDIR/$FILE -ref $REFERENCE -out $SDIR/fl$FILE -applyxfm -init $SDIR/$i
done

#
# create raw head template with flirt_average using already flirted images
#

FILES=""
COUNT=0
WHITELIST="/var/mri/fractional_anisotropy/txt/flirt_average_whitelist_2014-09-01.txt"

while read line
do
  set -- $line
  FILE=$(ls $SDIR | grep flc$line)
  if [ ! $FILE == "" ]; then
    FILES="$FILES $SDIR/$FILE"
    COUNT=$(($COUNT + 1)) 
  fi
done < $WHITELIST

echo $COUNT
echo $FILES
flirt_average $COUNT $FILES $SDIR/average_head.nii.gz -omat $SDIR/average_head.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear

```

### reorienting the domestic pig atlas
``` sh
# The domestic pig atlas of course is oriented "correctly" so the orientation
# had to be matched to the one we are using.
ATLAS=$1

fslorient -deleteorient $ATLAS

fslswapdim $ATLAS x -z -y $ATLAS

fslorient -setqformcode 1 $ATLAS
fslorient -setsformcode 1 $ATLAS

fslswapdim $ATLAS RL PA IS $ATLAS
```

``` sh
# splitting the domestic pig atlas into its single parts was done with fslmaths.
# Unfortunately, the linear transformation brought some artefacts into the atlas,
# since it's not possible to transform using only integer values.
for i in $(seq 0 251); do
  fslmaths $SDIR/$ATLAS -sub $i -thr 0 -uthr 1 $DDIR/"$i"_$ATLAS
done

```