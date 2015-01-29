# applying a cosine transform to the direction
# matrix of Nifti images. Swapping A->P with I->S

import numpy as np
import sys

# define transformation matrix
transform_matrix = np.matrix('1 0 0 0; 0 0 1 0; 0 -1 0 0; 0 0 0 1')

# transformation in separate method
def transform_nifti(path, transformation):
    import nibabel
    import numpy as np

    # load nifti
    image = nibabel.load(path)
    # get direction matrix
    affine = image.get_affine()
    # multiply with transformation matrix
    affine = affine.dot(transformation)
    # set result as qform / sform
    image.set_qform(affine)
    image.set_sform(affine)
    # save nifti, overwrites original!
    nibabel.save(image, path)

transform_nifti(sys.argv[1], transform_matrix)
print 'transformed subject: {0}'.format(sys.argv[1])
