/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_Mac_201501/bin/BRAINSResample \
	--interpolationMode NearestNeighbor  \
	--warpTransform Identity \
	--outputVolume resampledT2.nii.gz \
	--inputVolume /Shared/johnsonhj/HDNI/20150416_MiniPigData/M268P100_20130606/M268P100_20130606_T2TSE2mm.nii  \
	--referenceVolume  /Shared/johnsonhj/HDNI/20150416_MiniPigData/M268P100_20130606/M268P100_20130606_3DT1TFEhrs.nii 

/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_Mac_201501/bin/BRAINSMultiModeSegment \
	--inputVolumes /Shared/johnsonhj/HDNI/20150416_MiniPigData/M268P100_20130606/M268P100_20130606_3DT1TFEhrs.nii \
	--inputVolumes ./resampledT2.nii.gz  \
	--lowerThreshold 0.4,0.05 \
	--upperThreshold 1.0,0.85  \
	--outputROIMaskVolume output_WM_seg.nii.gz

/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_Mac_201501/bin/BRAINSMultiModeSegment \
	--inputVolumes /Shared/johnsonhj/HDNI/20150416_MiniPigData/M268P100_20130606/M268P100_20130606_3DT1TFEhrs.nii \
	--inputVolumes ./resampledT2.nii.gz  \
	--lowerThreshold 0.01,0.05 \
	--upperThreshold 0.4,0.9  \
	--outputROIMaskVolume output_GM_seg.nii.gz

/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_Mac_201501/bin/BRAINSMultiModeSegment \
	--inputVolumes /Shared/johnsonhj/HDNI/20150416_MiniPigData/M268P100_20130606/M268P100_20130606_3DT1TFEhrs.nii \
	--inputVolumes ./resampledT2.nii.gz  \
	--lowerThreshold 0.00,0.9 \
	--upperThreshold 0.3,1  \
	--outputROIMaskVolume output_CSF_seg.nii.gz
