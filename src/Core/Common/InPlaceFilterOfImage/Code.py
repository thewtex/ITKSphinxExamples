#!/usr/bin/env python

# Copyright NumFOCUS
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

import sys
import itk

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <filename>")
    sys.exit(1)
input_filename = sys.argv[1]

image = itk.imread(input_filename)

thresholded_in_place = itk.binary_threshold_image_filter(
    image,
    lower_threshold=10,
    upper_threshold=50,
    inside_value=255,
    outside_value=0,
    in_place=True,
)

print(image)
print(thresholded_in_place)
print(image == thresholded_in_place)
print(image is thresholded_in_place)
print(dir(image.GetPixelContainer()))
print(image.GetPixelContainer() == thresholded_in_place.GetPixelContainer())
