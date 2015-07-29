import sys
import os
import errno

if len(sys.argv) != 1:
    print("""ERROR:  Improper invocation

{0} <Experiment.json>

* The experiment json contains the parameters needed to
* dynamically scale the images (use slicer to determine approprate ranges)
* and to define the output image space to use.
* For Example (NOTE: Use full paths)
== Pig1.json
""".format(sys.argv[0])
)

def addToSysPath(index, path):
    if path not in sys.path:
        sys.path.insert(index, path)

# Modify the PATH for python modules
addToSysPath(0, '/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_OSX_20150619/NIPYPE')
#addToSysPath(0, '/scratch/johnsonhj/src/NEP-11/BRAINSTools/AutoWorkup/SEMTools')
addToSysPath(1, '/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_OSX_20150619/BRAINSTools/AutoWorkup')
addToSysPath(1, '/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_OSX_20150619/BRAINSTools')

# Modify the PATH for executibles used
temp_paths = os.environ['PATH'].split(os.pathsep)
temp_paths.insert(0, os.path.join('/Shared/sinapse/scratch/eunyokim/src/NamicExternal/build_OSX_20150619/', 'bin'))
os.environ['PATH'] = os.pathsep.join(temp_paths)

print(sys.path)

import SimpleITK as sitk
import matplotlib as mp

import nipype
from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory
from nipype.interfaces.base import traits, isdefined, BaseInterface
from nipype.interfaces.utility import Merge, Split, Function, Rename, IdentityInterface
import nipype.interfaces.io as nio  # Data i/o
import nipype.pipeline.engine as pe  # pypeline engine
from nipype.interfaces.ants import (
    Registration,
    ApplyTransforms,
    AverageImages, MultiplyImages,
    AverageAffineTransform)

from nipype.interfaces.semtools import *

import yaml

## Using yaml to load keys and values as strings

with open(sys.argv[1],'r') as paramFptr:
   ExperimentInfo = yaml.safe_load(paramFptr)

print ExperimentInfo
# del WDIR

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


minipigWF = pe.Workflow(name='MINIPIG_'+ExperimentInfo["Subject"]["UID"])
minipigWF.base_dir = ExperimentInfo["Atlas"]["TEMP_CACHE"]
mkdir_p(ExperimentInfo["Atlas"]["TEMP_CACHE"])

minipigWF.config['execution'] = {
    'plugin': 'Linear',
    # 'stop_on_first_crash':'true',
    # 'stop_on_first_rerun': 'true',
    'stop_on_first_crash': 'false',
    'stop_on_first_rerun': 'false',
# This stops at first attempt to rerun, before running, and before deleting previous results.
    'hash_method': 'timestamp',
    'single_thread_matlab': 'true',  # Multi-core 2011a  multi-core for matrix multip  lication.
    'remove_unnecessary_outputs': 'false',
    'use_relative_paths': 'false',  # relative paths should be on, require hash updat  e when changed.
    'remove_node_directories': 'false',  # Experimental
    'local_hash_check': 'true',
    'job_finished_timeout': 45
}
minipigWF.config['logging'] = {
    'workflow_level': 'DEBUG',
    'filemanip_level': 'DEBUG',
    'interface_level': 'DEBUG',
    'log_directory': ExperimentInfo["Atlas"]["LOG_DIR"]
}

input_spec = pe.Node(interface=IdentityInterface(
    fields=['Raw_Atlas', 'Raw_T1', 'Cropped_T1', 'Raw_T2', 'Raw_BrainMask', 'DomesticLUT', 'Domestic_LabelMap']),
                     run_without_submitting=True,
                     name='inputspec')

input_spec.inputs.Raw_T1 = ExperimentInfo["Subject"]["Raw_T1"]
input_spec.inputs.Raw_T2 = ExperimentInfo["Subject"]["Raw_T2"]
input_spec.inputs.Raw_BrainMask = ExperimentInfo["Subject"]["Raw_BrainMask"]
input_spec.inputs.Cropped_T1 = ExperimentInfo["Subject"]["Cropped_T1"]

input_spec.inputs.Raw_Atlas = ExperimentInfo["Atlas"]["IntensityImage"]
input_spec.inputs.DomesticLUT = ExperimentInfo["Atlas"]["LabelMapLUT"]
input_spec.inputs.Domestic_LabelMap = ExperimentInfo["Atlas"]["LabelMapImage"]


def ChangeDynamicRangeOfImage(inFN, outFN, winMin, winMax, outMin, outMax):
    import SimpleITK as sitk
    import os

    at = sitk.ReadImage(inFN)
    out_at = sitk.IntensityWindowing(at, windowMinimum=winMin, windowMaximum=winMax, outputMinimum=outMin,
                                     outputMaximum=outMax)
    out_at = sitk.Cast(out_at, sitk.sitkUInt16)
    sitk.WriteImage(out_at, outFN)
    return os.path.realpath(outFN)


domesticAtlasDynFix = pe.Node(
    Function(function=ChangeDynamicRangeOfImage, input_names=['inFN', 'outFN', 'winMin', 'winMax', 'outMin', 'outMax'],
             output_names=['outFN']),
    run_without_submitting=True, name="FixAtlas_DynFix")
domesticAtlasDynFix.inputs.outFN = 'ghost_fixed_dynamic_range.nii.gz'
domesticAtlasDynFix.inputs.winMin = ExperimentInfo["Atlas"]["IntensityWindowMin"]  # 8000
domesticAtlasDynFix.inputs.winMax = ExperimentInfo["Atlas"]["IntensityWindowMax"]  # 17000
domesticAtlasDynFix.inputs.outMin = 0
domesticAtlasDynFix.inputs.outMax = 4096
minipigWF.connect(input_spec, 'Raw_Atlas', domesticAtlasDynFix, 'inFN')

T1DynFix = pe.Node(
    Function(function=ChangeDynamicRangeOfImage, input_names=['inFN', 'outFN', 'winMin', 'winMax', 'outMin', 'outMax'],
             output_names=['outFN']),
    run_without_submitting=True, name="T1DynFix")
T1DynFix.inputs.outFN = 'Cropped_T1_DynamicRange.nii.gz'
T1DynFix.inputs.winMin = ExperimentInfo["Subject"]["T1WindowMin"]  # 300
T1DynFix.inputs.winMax = ExperimentInfo["Subject"]["T1WindowMax"]  # 1500
T1DynFix.inputs.outMin = 0
T1DynFix.inputs.outMax = 4096
minipigWF.connect(input_spec, 'Cropped_T1', T1DynFix, 'inFN')

T2DynFix = pe.Node(
    Function(function=ChangeDynamicRangeOfImage, input_names=['inFN', 'outFN', 'winMin', 'winMax', 'outMin', 'outMax'],
             output_names=['outFN']),
    run_without_submitting=True, name="T2DynFix")
T2DynFix.inputs.outFN = 'T2_DynamicRange.nii.gz'
T2DynFix.inputs.winMin = ExperimentInfo["Subject"]["T2WindowMin"]  # 200
T2DynFix.inputs.winMax = ExperimentInfo["Subject"]["T2WindowMax"]  # 2300
T2DynFix.inputs.outMin = 0
T2DynFix.inputs.outMax = 4096
minipigWF.connect(input_spec, 'Raw_T2', T2DynFix, 'inFN')

ResampleBrainMask = pe.Node(BRAINSResample(), name="ResampleBrainMask")
ResampleBrainMask.inputs.pixelType = 'binary'
ResampleBrainMask.inputs.outputVolume = 'ResampledBrainMask.nii.gz'

minipigWF.connect(input_spec, 'Raw_BrainMask', ResampleBrainMask, 'inputVolume')
minipigWF.connect(T1DynFix, 'outFN', ResampleBrainMask, 'referenceVolume')


def SmoothBrainMask(inFN, outFN):
    import SimpleITK as sitk
    import os

    FIXED_BM = inFN
    fbm = sitk.ReadImage(FIXED_BM) > 0  # Make binary

    ## A smoothing operation to get rid of rough brain edges
    fbm = sitk.BinaryErode(fbm, 1)
    fbm = sitk.BinaryDilate(fbm, 2)
    fbm = sitk.BinaryErode(fbm, 1)
    sitk.WriteImage(sitk.Cast(fbm, sitk.sitkUInt16), outFN)
    return os.path.realpath(outFN)


smoothBrainMask = pe.Node(Function(function=SmoothBrainMask, input_names=['inFN', 'outFN'], output_names=['outFN']),
                          run_without_submitting=True, name="smoothBrainMask")
smoothBrainMask.inputs.outFN = "smoothedBrainMask.nii.gz"

minipigWF.connect(ResampleBrainMask, 'outputVolume', smoothBrainMask, 'inFN')

######===========================
T2_to_T1_Fit = pe.Node(BRAINSFit(), name="T2_to_T1_Fit")
T2_to_T1_Fit.inputs.samplingPercentage = .10
T2_to_T1_Fit.inputs.outputTransform = 'T2_to_T1.h5'
                                     #Rigid < ScaleVersor3D < ScaleSkewVersor3D < Affine < (BSpline | SyN)
T2_to_T1_Fit.inputs.transformType = ['Rigid','ScaleVersor3D','ScaleSkewVersor3D','Affine'] #Use affine registration to fit T2 to T1 due to susceptibility argifact distortion
T2_to_T1_Fit.inputs.costMetric = 'MMI'
T2_to_T1_Fit.inputs.numberOfMatchPoints = 20
T2_to_T1_Fit.inputs.numberOfHistogramBins = 50
T2_to_T1_Fit.inputs.minimumStepLength = 0.0001
T2_to_T1_Fit.inputs.outputVolume = 'T2inT1.nii.gz'
T2_to_T1_Fit.inputs.outputVolumePixelType = 'int'
T2_to_T1_Fit.inputs.interpolationMode = 'BSpline'
T2_to_T1_Fit.inputs.initializeTransformMode = 'Off'

minipigWF.connect(T1DynFix, 'outFN', T2_to_T1_Fit, 'fixedVolume')
minipigWF.connect(T2DynFix, 'outFN', T2_to_T1_Fit, 'movingVolume')

## No masking needed, these should be topologically equivalent in all spaces
## T2_to_T1_Fit.inputs.maskProcessingMode="ROI"
## minipigWF.connect( smoothBrainMask, 'outFN',T2_to_T1_Fit,'fixedBinaryVolume')
#  T2_to_T1_Fit.inputs.initializeTransformMode useMomentsAlign
#  T2_to_T1_Fit.inputs.interpolationMode ResampleInPlace \
#  T2_to_T1_Fit.inputs.fixedBinaryVolume ${SMOOTHEDBM} \
#  T2_to_T1_Fit.inputs.maskProcessingMode ROI \


######===========================
def ChopImage(inFN, inMaskFN, outFN):
    """A function to apply mask to zero out all non-interesting pixels.
       ideally this should not be needed, but in an attempt to figure out
       why registration is acting difficult, this is a reasonable solution
    """
    import SimpleITK as sitk
    import os

    fbm = sitk.ReadImage(inMaskFN) > 0
    int1 = sitk.ReadImage(inFN)
    int1_mask = sitk.Cast(int1 > 0, sitk.sitkUInt16)
    outt1 = sitk.Cast(int1, sitk.sitkUInt16) * sitk.Cast(fbm, sitk.sitkUInt16) * int1_mask

    sitk.WriteImage(outt1, outFN)
    return os.path.realpath(outFN)


brainExtractT1 = pe.Node(Function(function=ChopImage, input_names=['inFN', 'inMaskFN', 'outFN'], output_names=['outFN']),
                 run_without_submitting=True, name="brainExtractT1")
brainExtractT1.inputs.outFN = 'T1_CHOPPED.nii.gz'
minipigWF.connect(T1DynFix, 'outFN', brainExtractT1, 'inFN')
minipigWF.connect(smoothBrainMask, 'outFN', brainExtractT1, 'inMaskFN')

brainExtractT2 = pe.Node(Function(function=ChopImage, input_names=['inFN', 'inMaskFN', 'outFN'], output_names=['outFN']),
                 run_without_submitting=True, name="brainExtractT2")
brainExtractT2.inputs.outFN = 'T2_CHOPPED.nii.gz'
minipigWF.connect(T2_to_T1_Fit, 'outputVolume', brainExtractT2, 'inFN')
minipigWF.connect(smoothBrainMask, 'outFN', brainExtractT2, 'inMaskFN')

######===========================
AT_to_T1_Fit = pe.Node(BRAINSFit(), name="AT_to_T1_Fit")
AT_to_T1_Fit.inputs.samplingPercentage = .15
AT_to_T1_Fit.inputs.outputTransform = 'AT_to_T1.h5'
AT_to_T1_Fit.inputs.useRigid = True
AT_to_T1_Fit.inputs.useScaleVersor3D = True
AT_to_T1_Fit.inputs.useAffine = True
AT_to_T1_Fit.inputs.costMetric = 'MMI'
AT_to_T1_Fit.inputs.numberOfMatchPoints = 20
AT_to_T1_Fit.inputs.numberOfHistogramBins = 50
AT_to_T1_Fit.inputs.minimumStepLength = [0.001, 0.0001, 0.0001]
AT_to_T1_Fit.inputs.outputVolume = 'AT_to_T1.nii.gz'
AT_to_T1_Fit.inputs.outputVolumePixelType = 'int'
### AT_to_T1_Fit.inputs.interpolationMode='BSpline'
AT_to_T1_Fit.inputs.initializeTransformMode = 'useMomentsAlign'  # 'useGeometryAlign'
### AT_to_T1_Fit.inputs.maskProcessingMode="ROIAUTO"  ## Images are choppped already, so ROIAUTO should work
### AT_to_T1_Fit.inputs.ROIAutoClosingSize=2  ## Mini pig brains are much smalle than human brains
### AT_to_T1_Fit.inputs.ROIAutoDilateSize=.5  ## Auto dilate a very small amount

minipigWF.connect(brainExtractT1, 'outFN', AT_to_T1_Fit, 'fixedVolume')
minipigWF.connect(domesticAtlasDynFix, 'outFN', AT_to_T1_Fit, 'movingVolume')

######===========================
Atlas2Subject_SyN = pe.Node(interface=Registration(), name="antsA2S")
##many_cpu_sge_options_dictionary = {'qsub_args': modify_qsub_args(CLUSTER_QUEUE,8,8,24), 'overwrite': True}
##ComputeAtlasToSubjectTransform.plugin_args = many_cpu_sge_options_dictionary

Atlas2Subject_SyN.inputs.dimension = 3
""" This is the recommended set of parameters from the ANTS developers """
Atlas2Subject_SyN.inputs.output_transform_prefix = 'A2S_output_tfm'
Atlas2Subject_SyN.inputs.transforms = ["Affine", "SyN", "SyN", "SyN"]
Atlas2Subject_SyN.inputs.transform_parameters = [[0.1], [0.1, 3.0, 0.0], [0.1, 3.0, 0.0], [0.1, 3.0, 0.0]]
Atlas2Subject_SyN.inputs.metric = ['MI', 'CC', 'CC', 'CC']
Atlas2Subject_SyN.inputs.sampling_strategy = ['Regular', None, None, None]
Atlas2Subject_SyN.inputs.sampling_percentage = [0.27, .8, .8, .8]
Atlas2Subject_SyN.inputs.metric_weight = [1.0, 1.0, 1.0, 1.0]
Atlas2Subject_SyN.inputs.radius_or_number_of_bins = [32, 3, 3, 3]
Atlas2Subject_SyN.inputs.number_of_iterations = [[1000, 1000, 1000, 1000], [1000, 250], [140], [25]]
Atlas2Subject_SyN.inputs.convergence_threshold = [5e-8, 5e-7, 5e-6, 5e-4]
Atlas2Subject_SyN.inputs.convergence_window_size = [10, 10, 10, 10]
Atlas2Subject_SyN.inputs.use_histogram_matching = [True, True, True, True]
Atlas2Subject_SyN.inputs.shrink_factors = [[8, 4, 2, 1], [8, 4], [2], [1]]
Atlas2Subject_SyN.inputs.smoothing_sigmas = [[3, 2, 1, 0], [3, 2], [1], [0]]
Atlas2Subject_SyN.inputs.sigma_units = ["vox", "vox", "vox", "vox"]
Atlas2Subject_SyN.inputs.use_estimate_learning_rate_once = [False, False, False, False]
Atlas2Subject_SyN.inputs.write_composite_transform = True
Atlas2Subject_SyN.inputs.collapse_output_transforms = False
Atlas2Subject_SyN.inputs.initialize_transforms_per_stage = True
Atlas2Subject_SyN.inputs.winsorize_lower_quantile = 0.01
Atlas2Subject_SyN.inputs.winsorize_upper_quantile = 0.99
Atlas2Subject_SyN.inputs.output_warped_image = 'atlas2subject.nii.gz'
Atlas2Subject_SyN.inputs.output_inverse_warped_image = 'subject2atlas.nii.gz'
Atlas2Subject_SyN.inputs.save_state = 'SavedAtlas2Subject_SyNSyNState.h5'
Atlas2Subject_SyN.inputs.float = True
Atlas2Subject_SyN.inputs.args = "--verbose"

minipigWF.connect(brainExtractT2,   'outFN', Atlas2Subject_SyN, "fixed_image")
minipigWF.connect(domesticAtlasDynFix, 'outFN', Atlas2Subject_SyN, "moving_image")
minipigWF.connect(AT_to_T1_Fit, 'outputTransform', Atlas2Subject_SyN, 'initial_moving_transform')

######===========================
def MakeVector(inFN1, inFN2=None):
    print "inFN1: {0}".format(inFN1)
    print "inFN2: {0}".format(inFN2)
    if inFN2 == None:
        return inFN1
    else:
        return [inFN1, inFN2]


SubjectMakeVector = pe.Node(Function(function=MakeVector, input_names=['inFN1', 'inFN2'], output_names=['outFNs']),
                            run_without_submitting=True, name="SubjectMakeVector")
minipigWF.connect(brainExtractT1, 'outFN', SubjectMakeVector, 'inFN1')
minipigWF.connect(brainExtractT2, 'outFN', SubjectMakeVector, 'inFN2')

AtlasMakeVector = pe.Node(Function(function=MakeVector, input_names=['inFN1', 'inFN2'], output_names=['outFNs']),
                          run_without_submitting=True, name="AtlasMakeVector")
minipigWF.connect(domesticAtlasDynFix, 'outFN', AtlasMakeVector, 'inFN1')
minipigWF.connect(domesticAtlasDynFix, 'outFN', AtlasMakeVector, 'inFN2')

######===========================
##### NOTE THAT DOMESTIC PIG DOES NOT HAVE T2. 
Atlas2Subject_SyN2 = pe.Node(interface=Registration(), name="antsA2SMultiModal")
##many_cpu_sge_options_dictionary = {'qsub_args': modify_qsub_args(CLUSTER_QUEUE,8,8,24), 'overwrite': True}
##ComputeAtlasToSubjectTransform.plugin_args = many_cpu_sge_options_dictionary

Atlas2Subject_SyN2.inputs.dimension = 3
Atlas2Subject_SyN2.inputs.output_transform_prefix = 'A2S_output_tfm'
Atlas2Subject_SyN2.inputs.transforms = ["SyN"]
Atlas2Subject_SyN2.inputs.transform_parameters = [[0.1, 3.0, 0.0]]
Atlas2Subject_SyN2.inputs.metric = ['CC']
Atlas2Subject_SyN2.inputs.sampling_strategy = [None]
Atlas2Subject_SyN2.inputs.sampling_percentage = [.5]
Atlas2Subject_SyN2.inputs.metric_weight = [1.0]
Atlas2Subject_SyN2.inputs.radius_or_number_of_bins = [3]
Atlas2Subject_SyN2.inputs.number_of_iterations = [[25]]
Atlas2Subject_SyN2.inputs.convergence_threshold = [5e-3]
Atlas2Subject_SyN2.inputs.convergence_window_size = [10]
Atlas2Subject_SyN2.inputs.use_histogram_matching = [True]
Atlas2Subject_SyN2.inputs.shrink_factors = [[1]]
Atlas2Subject_SyN2.inputs.smoothing_sigmas = [[0]]
Atlas2Subject_SyN2.inputs.sigma_units = ["vox"]
Atlas2Subject_SyN2.inputs.use_estimate_learning_rate_once = [False]
Atlas2Subject_SyN2.inputs.write_composite_transform = True
Atlas2Subject_SyN2.inputs.collapse_output_transforms = False
Atlas2Subject_SyN2.inputs.initialize_transforms_per_stage = True
Atlas2Subject_SyN2.inputs.winsorize_lower_quantile = 0.01
Atlas2Subject_SyN2.inputs.winsorize_upper_quantile = 0.99
Atlas2Subject_SyN2.inputs.output_warped_image = 'atlas2subjectMultiModal.nii.gz'
Atlas2Subject_SyN2.inputs.output_inverse_warped_image = 'subject2atlasMultiModal.nii.gz'
Atlas2Subject_SyN2.inputs.save_state = 'SavedAtlas2Subject_SyNSyNState.h5'
Atlas2Subject_SyN2.inputs.float = True
Atlas2Subject_SyN2.inputs.args = "--verbose"

minipigWF.connect(SubjectMakeVector, 'outFNs', Atlas2Subject_SyN2, "fixed_image")
minipigWF.connect(AtlasMakeVector, 'outFNs', Atlas2Subject_SyN2, "moving_image")
minipigWF.connect(Atlas2Subject_SyN, 'save_state', Atlas2Subject_SyN2, 'restore_state')


######===========================
def getListIndex(imageList, index):
    return imageList[index]


ResampleLabelMap = pe.Node(BRAINSResample(), name="ResampleLabelMap")

ResampleLabelMap.inputs.pixelType = 'ushort'
ResampleLabelMap.inputs.interpolationMode = 'NearestNeighbor'
ResampleLabelMap.inputs.outputVolume = 'ResampleLabelMap.nii.gz'
minipigWF.connect([(Atlas2Subject_SyN2, ResampleLabelMap, [(('composite_transform', getListIndex, 0), 'warpTransform')])])

minipigWF.connect(input_spec, 'Domestic_LabelMap', ResampleLabelMap, 'inputVolume')
minipigWF.connect(T1DynFix, 'outFN', ResampleLabelMap, 'referenceVolume')

datasink = pe.Node(nio.DataSink(), name='sinker')
datasink.inputs.base_directory = os.path.join(ExperimentInfo["Subject"]["ResultDir"],ExperimentInfo["Subject"]["UID"])
minipigWF.connect(ResampleLabelMap, 'outputVolume', datasink, '@outputAtlasLabelMapWarped')
#minipigWF.connect(Atlas2Subject_SyN2, 'output_warped_image', datasink, '@outputAtlasWarped')
minipigWF.connect(T1DynFix, 'outFN', datasink, '@T1Fixed')
minipigWF.connect(T2DynFix, 'outFN', datasink, '@T2Fixed')
minipigWF.connect(brainExtractT1, 'outFN', datasink, '@T1Chopped')
minipigWF.connect(brainExtractT2, 'outFN', datasink, '@T2Chopped')
minipigWF.connect(input_spec,'DomesticLUT',datasink,'@DomesticLUT')

#minipigWF.write_graph(dotfilename='graph.dot', graph2use='flat', format='svg', simple_form=True)

minipigWF.run()
