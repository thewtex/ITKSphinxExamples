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
# ./SegmentWithWatershedAndDistanceMap.py <InputImageFile>
# <ReversedInputImageFile> <DistanceMapOutputImageFile>
# <WatershedOutputFileName> <SegmentationResultOutputImageFile>
# BinarizingRadius MajorityThreshold WatershedThreshold WatershedLevel
# CleaningStructuringElementRadius
# e.g.
# ./SegmentWithWatershedAndDistanceMap.py PlateauBorder.tif
# reversedInputImage.tif distanceMap.tif watershed.tif segmentationResult.tif
# 2 2 0.01 0.5 3
# (A rule of thumb is to set the Threshold to be about 1 / 100 of the Level.)
#
#  threshold: absolute minimum height value used during processing.
#        Raising this threshold percentage effectively decreases the number of local minima in the input,
#        resulting in an initial segmentation with fewer regions.
#        The assumption is that the shallow regions that thresholding removes are of of less interest.
#  level: controls the depth of metaphorical flooding of the image.
#        That is, it sets the maximum saliency value of interest in the result.
#        Raising and lowering the Level influences the number of segments
#        in the basic segmentation that are merged to produce the final output.
#        A level of 1.0 is analogous to flooding the image up to a
#        depth that is 100 percent of the maximum value in the image.
#        A level of 0.0 produces the basic segmentation, which will typically be very oversegmented.
#        Level values of interest are typically low (i.e. less than about 0.40 or 40%),
#        since higher values quickly start to undersegment the image.

import sys
import itk

import numpy as np


if len(sys.argv) != 11:
    print('Usage: ' + sys.argv[0] +
          ' <InputFileName> <ReversedInputOutputFileName>\
          <DistanceMapOutputFileName> <WatershedOutputFileName>\
          <SegmentationResultOutputImageFile> <BinarizingRadius>\
          <MajorityThreshold> <WatershedThreshold> <Level>\
          <CleaningStructuringElementRadius>')
    sys.exit(1)

inputFileName = sys.argv[1]
reversedInputOutputFileName = sys.argv[2]
distanceMapOutputFileName = sys.argv[3]
watershedOutputFileName = sys.argv[4]
segmentationResultOutputImageFile = sys.argv[5]

Dimension = 3

UCharPixelType = itk.ctype('unsigned char')
InputImageType = itk.Image[UCharPixelType, Dimension]

FloatPixelType = itk.ctype('float')
FloatImageType = itk.Image[FloatPixelType, Dimension]

RGBPixelType = itk.RGBPixel[UCharPixelType]
RGBImageType = itk.Image[RGBPixelType, Dimension]


reader = itk.ImageFileReader[InputImageType].New()
reader.SetFileName(inputFileName)

stack_image = reader.GetOutput()


# Create bubble image: get a binarized version of the input image
VotingBinaryIterativeHoleFillingImageFilterType = \
    itk.VotingBinaryIterativeHoleFillingImageFilter[InputImageType]
votingBinaryHoleFillingImageFilter = \
    VotingBinaryIterativeHoleFillingImageFilterType.New()
votingBinaryHoleFillingImageFilter.SetInput(reader.GetOutput())

binarizingRadius = int(sys.argv[6])

indexRadius = itk.Size[Dimension]()
indexRadius.Fill(binarizingRadius)

votingBinaryHoleFillingImageFilter.SetRadius(indexRadius)

votingBinaryHoleFillingImageFilter.SetBackgroundValue(0)
votingBinaryHoleFillingImageFilter.SetForegroundValue(255)

majorityThreshold = int(sys.argv[7])
votingBinaryHoleFillingImageFilter.SetMajorityThreshold(majorityThreshold)

votingBinaryHoleFillingImageFilter.Update()

bubble_image = votingBinaryHoleFillingImageFilter.GetOutput()

# Write bubble image
WriterType = itk.ImageFileWriter[InputImageType]
writer = WriterType.New()
writer.SetFileName(reversedInputOutputFileName)
writer.SetInput(bubble_image)
writer.Update()


# Watershed on bubbles
Dimension = len(np.shape(bubble_image))

# Convert to itk array and normalize
multiplyImageFilterFilter = \
    itk.MultiplyImageFilter[InputImageType, InputImageType, FloatImageType].New(Input=bubble_image)
multiplyImageFilterFilter.SetConstant(255.0)

multiplyImageFilterFilter.Update()

bubble_image_preclamp = multiplyImageFilterFilter.GetOutput()

clampFilter = \
    itk.ClampImageFilter[FloatImageType, FloatImageType].New(Input=bubble_image_preclamp)
clampFilter.SetBounds(0, 255)

bubble_image_clamp = clampFilter.Update()

itk_vol_img = clampFilter.GetOutput()


# Get the distance map of the input image
distanceMapImageFilter = \
    itk.SignedMaurerDistanceMapImageFilter[FloatImageType, FloatImageType].New(Input=itk_vol_img)
distanceMapImageFilter.SetInsideIsPositive(False)
distanceMapImageFilter.Update()


WriterType = itk.ImageFileWriter[RGBImageType]
writer = WriterType.New()
writer.SetFileName(distanceMapOutputFileName)
writer.SetInput(distanceMapImageFilter.GetOutput())
writer.Update()


# Apply the watershed segmentation
watershedTreshold = sys.argv[8]
watershedLevel = sys.argv[9]

watershed = itk.WatershedImageFilter.New(Input=distanceMapImageFilter.GetOutput())
watershed.SetThreshold(watershedTreshold)
watershed.SetLevel(watershedLevel)
watershed.Update()

distanceMapArray = itk.GetArrayFromImage(distanceMapImageFilter)
watershedArray = itk.GetArrayFromImage(watershed)


WriterType = itk.ImageFileWriter[RGBImageType]
writer = WriterType.New()
writer.SetFileName(watershedOutputFileName)
writer.SetInput(watershed.GetOutput())
writer.Update()


# Clean the segmentation image: remove small objects by performing an
# opening morphological operation
LabeledImageType = type(watershed.GetOutput())
StructuringElementType = \
    itk.BinaryBallStructuringElement[LabeledImageType.PixelType, LabeledImageType.ImageDimension]
structuringElement = StructuringElementType

cleaningStructuringElementRadius = sys.argv[10]
structuringElement.SetRadius(cleaningStructuringElementRadius)
structuringElement.CreateStructuringElement()

BinaryMorphologicalOpeningImageFilterType = \
    itk.BinaryMorphologicalOpeningImageFilter[LabeledImageType, LabeledImageType, StructuringElementType]
openingFilter = BinaryMorphologicalOpeningImageFilterType.New()
openingFilter.SetInput(watershed.GetOutput())
openingFilter.SetKernel(structuringElement)
openingFilter.Update()


WriterType = itk.ImageFileWriter[RGBImageType]
writer = WriterType.New()
writer.SetFileName(segmentationResultOutputImageFile)
writer.SetInput(openingFilter.GetOutput())
writer.Update()
