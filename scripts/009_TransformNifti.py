import numpy as np
import sys
transform_matrix = np.matrix('1 0 0 0; 0 0 1 0; 0 -1 0 0; 0 0 0 1')

def transform_nifti(path, transformation):
    import nibabel
    import numpy as np

    image = nibabel.load(path)
    affine = image.get_affine()
    affine = affine.dot(transformation)
    image.set_qform(affine)
    image.set_sform(affine)
    nibabel.save(image, path)

transform_nifti(sys.argv[1], transform_matrix)
print 'transformed subject: {0}'.format(sys.argv[1])
