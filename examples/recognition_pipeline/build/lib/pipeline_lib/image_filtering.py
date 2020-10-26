"""
  Copyright 2020 Google LLC
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
 
    https://www.apache.org/licenses/LICENSE-2.0
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

PREREQUISITES_MAP = {'Google_Vision_API': {'format':['JPEG', 'PNG8', 'PNG24', 'GIF', 'BMP', 'WEBP', 'RAW', 'ICO', 'PDF', 'TIFF'], 'minimun_size':'300'}}

def is_eligible(image, provider):
    """ Checks if the image is eligible for being labeled by the provider.

    For each criteria of the providers requirements, checks if the image's attributes match the providers prerequisites.
    """
    for key, value in PREREQUISITES_MAP[provider].items():
        if not is_supported(image['image_attributes'][key], key, value): # TODO: check if this is how tal named the map.
            return False
    return True

def is_supported(image_attribute, criteria, prerequisites):
    """ Checks if the images arribute is supported by the provider's prerequisites for a specific criteria.
    """
    # TODO: not fully implemnted yet. Should it be switch-case for each different condition? need to make sure it is ok that all prequisites are of the same.
    if criteria == 'format':
        return image_attribute in prerequisites
    if criteria == 'resolution':
        return image_attribute >= prerequisites
    return True
