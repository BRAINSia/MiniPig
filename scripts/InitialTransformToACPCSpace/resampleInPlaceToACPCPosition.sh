/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_Mac_201501/bin/BRAINSResample  \
	--inputVolume ./M268P100_20130606_3DT1TFEhrs.nii.gz \
	--outputVolume ./t1_rotated.nii.gz \
	--interpolationMode ResampleInPlace \
	--warpTransform pi_transform.h5

/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_Mac_201501/bin/BRAINSResample  \
	--inputVolume ./M268P100_20130606_T2TSE2mmSENSE.nii.gz  \
	--outputVolume ./t2_rotated.nii.gz \
	--interpolationMode ResampleInPlace \
	--warpTransform pi_transform.h5

