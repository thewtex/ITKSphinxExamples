#!/usr/bin/env python

# Copyright Insight Software Consortium
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Run with:
# ./segmentation_result_visualization.py <>
# e.g.
# ./segmentation_result_visualization.py P
#
# This is a companion code to the SegmentWithWatershedAndDistanceMap example
# to generate the example segmentation results visualizations.
#
#  threshold:  is used to set the absolute minimum height value used during processing.
#        Raising this threshold percentage effectively decreases the number of local minima in the input,
#        resulting in an initial segmentation with fewer regions.
#        The assumption is that the shallow regions that thresholding removes are of of less interest.
#  level: parameter controls the depth of metaphorical flooding of the image.
#        That is, it sets the maximum saliency value of interest in the result.


import sys
import itk

import matplotlib.pyplot as plt
import numpy as np


if len(sys.argv) != 5:
    print('Usage: ' + sys.argv[0] +
          ' <InputFileName> <BubbleFileName> <DistanceMapFileName>\
          <WatershedOutputFileName> <CleanSegmentationFileName>\
          <InputProjectionsOutputFileName> <PipelineImagesOutputFileName>\
          <SegmentationProjectionsOutputFileName>\
          <CleanSegmentationProjectionsOutputFileName>\
          <VolumeRenderingOutputFileName>')
    sys.exit(1)



reader = itk.ImageFileReader[FloatImageType].New()
reader.SetFileName(inputFileName)

stack_image = reader.GetOutput()


# Display the input image projections
fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize = (12, 4))
for i, (cax, clabel) in enumerate(zip([ax1, ax2, ax3], ['xy', 'zy', 'zx'])):
    cax.imshow(np.sum(stack_image,i).squeeze(), interpolation='none', cmap = 'bone_r')
    cax.set_title('%s Projection' % clabel)
    cax.set_xlabel(clabel[0])
    cax.set_ylabel(clabel[1])

plt.save(InputProjectionsOutputFileName)


reader = itk.ImageFileReader[FloatImageType].New()
reader.SetFileName(inputFileName)

bubble_image = reader.GetOutput()

plt.imshow(bubble_image[5], cmap = 'bone')
plt.save(BubbleFileName)


# Cut-through: display the segmentation pipeline image results
# Show the values at a slice in the middle as a way to get a feeling for what
# the distance map and the watershed did

reader = itk.ImageFileReader[FloatImageType].New()
reader.SetFileName(WatershedOutputFileName)
ws_vol = reader.GetOutput()

reader = itk.ImageFileReader[FloatImageType].New()
reader.SetFileName(DistanceMapFileName)
dmap_vol = reader.GetOutput()


mid_slice = ws_vol.shape[0]//2
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (20, 7))
ax1.imshow(bubble_image[mid_slice], cmap ='bone')
ax1.set_title('Bubble Image')
m_val = np.abs(dmap_vol[mid_slice]).std()
ax2.imshow(dmap_vol[mid_slice], cmap = 'RdBu', vmin = -m_val, vmax = m_val)
ax2.set_title('Distance Image\nMin:%2.2f, Max:%2.2f, Mean: %2.2f' % (dmap_vol[mid_slice].min(),
                                                                    dmap_vol[mid_slice].max(),
                                                                    dmap_vol[mid_slice].mean()))
ax3.imshow(ws_vol[mid_slice], cmap = 'nipy_spectral')
ax3.set_title('Watershed\nLabels Found:{}'.format(len(np.unique(ws_vol[ws_vol>0]))));

plt.save(PipelineImagesOutputFileName)


# Show segmentation result projections
fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize = (12, 4))
for i, (cax, clabel) in enumerate(zip([ax1, ax2, ax3], ['xy', 'zy', 'zx'])):
    cax.imshow(np.max(ws_vol,i).squeeze(), interpolation='none', cmap = 'nipy_spectral')
    cax.set_title('%s Projection' % clabel)
    cax.set_xlabel(clabel[0])
    cax.set_ylabel(clabel[1])

plt.save(SegmentationProjectionsOutputFileName)


# Clean segmentation result projections
reader = itk.ImageFileReader[FloatImageType].New()
reader.SetFileName(CleanSegmentationFileName)

bubble_label_image = reader.GetOutput()

fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize = (12, 4))
for i, (cax, clabel) in enumerate(zip([ax1, ax2, ax3], ['xy', 'zy', 'zx'])):
    cax.imshow(np.max(bubble_label_image,i),
               interpolation='none',
               cmap = plt.cm.jet, vmin = 0, vmax = new_idx)
    cax.set_title('%s Projection' % clabel)
    cax.set_xlabel(clabel[0])
    cax.set_ylabel(clabel[1])

plt.save(CleanSegmentationProjectionsOutputFileName)


# Show 3D Rendering
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from skimage import measure
from tqdm import tqdm
def show_3d_mesh(image, thresholds):
    p = image[::-1].swapaxes(1,2)
    cmap = plt.cm.get_cmap('nipy_spectral_r')
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    for i, c_threshold in tqdm(list(enumerate(thresholds))):
        verts, faces, _, _ = measure.marching_cubes(p==c_threshold, 0)
        mesh = Poly3DCollection(verts[faces], alpha=0.25, edgecolor='none', linewidth = 0.1)
        mesh.set_facecolor(cmap(i / len(thresholds))[:3])
        mesh.set_edgecolor([1, 0, 0])
        ax.add_collection3d(mesh)

    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])

    ax.view_init(45, 45)
    return fig
_ = show_3d_mesh(bubble_label_image, range(1,np.max(bubble_label_image), 10))

# Write 3D rendering of segmented image
WriterType = itk.ImageFileWriter[RGBImageType]
writer = WriterType.New()
writer.SetFileName(VolumeRenderingOutputFileName)
writer.SetInput(mesh)
writer.Update()
