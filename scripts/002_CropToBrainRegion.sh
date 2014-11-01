# To remove the most non-brain tissue of 3DT1 images the images is
# cropped, using a text file containing the coordinates of the
# anterrior commissure and the fslroi script

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
