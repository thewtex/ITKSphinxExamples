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
# ./segmentation_result_analysis.py <>
# e.g.
# ./segmentation_result_analysis.py P
#
# This is a companion code to the SegmentWithWatershedAndDistanceMap example
# to generate the example segmentation results analysis visualizations.
#
#  threshold: used to set the absolute minimum height value used during processing.
#        Raising this threshold percentage effectively decreases the number of local minima in the input,
#  level: parameter controls the depth of metaphorical flooding of the image.
#        That is, it sets the maximum saliency value of interest in the result.


import sys

import numpy as np
import pandas as pd


if len(sys.argv) != 5:
    print('Usage: ' + sys.argv[0] +
          ' <CleanSegmentationFileName> <TrainingBubbleVolumeStatsFileName>\
          <BubbleVolumeStatsOutputFileName>\
          <BubbleVolumeStatsSampleTableOutputFileName>\
          <BubbleVolumeDensityStatsPlotOutputFileName>\
          <BubbleCentersPlotOutputFileName>\
          <BubbleStatsComparisonPlotOutputFileName>')
    sys.exit(1)


# Read segmentation image
reader = itk.ImageFileReader[FloatImageType].New()
reader.SetFileName(CleanSegmentationFileName)

bubble_label_image = reader.GetOutput()


# Calculate bubble centers
def meshgrid3d_like(in_img):
    return np.meshgrid(range(in_img.shape[1]),range(in_img.shape[0]), range(in_img.shape[2]))
zz, xx, yy = meshgrid3d_like(bubble_label_image)
out_results = []
for c_label in np.unique(bubble_label_image): # one bubble at a time
    if c_label>0: # ignore background
        cur_roi = bubble_label_image==c_label
        out_results += [{'x': xx[cur_roi].mean(), 'y': yy[cur_roi].mean(), 'z': zz[cur_roi].mean(),
                         'volume': np.sum(cur_roi)}]


# Write the bubble volume stats
out_table = pd.DataFrame(out_results)
out_table.to_csv(BubbleVolumeStatsOutputFileName) #'bubble_volume.csv'

# Write the bubble volume stats sample table
volume_sample = out_table.sample(5)
volume_sample.save(BubbleVolumeStatsSampleTableOutputFileName)

# Write the bubble volume density plot
bubble_volume_density = out_table['volume'].plot.density()
bubble_volume_density.save(BubbleVolumeDensityStatsPlotOutputFileName)

# Write the bubble center plot
bubble_centers_plot = out_table.plot.hexbin('x', 'y', gridsize = (5,5))
bubble_centers_plot.save(BubbleCentersPlotOutputFileName)


# Compare to the training values
train_values = pd.read_csv(TrainingBubbleVolumeStatsFileName) #'../input/bubble_volume.csv'

fig, (ax1, ax2) = plt.subplots(1,2, figsize = (8, 4))
_, n_bins, _ = ax1.hist(np.log10(train_values['volume']), bins = 20, label = 'Training Volumes')
ax1.hist(np.log10(out_table['volume']), n_bins, alpha = 0.5, label = 'Watershed Volumes')
ax1.legend()
ax1.set_title('Volume Comparison\n(Log10)')
ax2.plot(out_table['x'], out_table['y'], 'r.',
        train_values['x'], train_values['y'], 'b.')
ax2.legend(['Watershed Bubbles',
            'Training Bubbles'])

plt.save(BubbleStatsComparisonPlotOutputFileName)
