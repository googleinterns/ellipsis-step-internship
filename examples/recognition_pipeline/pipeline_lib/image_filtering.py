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

from filters.filter_by_format import FilterByFormat
from filters.filter_by_resolution import FilterByResolution

PREREQUISITES_MAP = {'Google_Vision_API': {'format': FilterByFormat(['JPEG', 'PNG8', 'PNG24', 'GIF', 'BMP', 'WEBP', 'RAW', 'ICO', 'PDF', 'TIFF']),\
                                           'resolution':FilterByResolution({'length':640, 'width': 480})}}

def is_eligible(image, provider):
    """ Checks if the image is eligible for being labeled by the provider.

    For each criteria of the providers requirements, checks if the image's attributes match the providers prerequisites.
    """
    for criteria, criteria_filter in PREREQUISITES_MAP[provider].items():
        if criteria not in image['imageAttributes'] or not criteria_filter.is_supported(image['imageAttributes'][criteria]): # TODO: check if this is how tal named the map.
             # If the image doesn't have this property stored or the property doesn't meet the perequisites then it is not supported.
            return False
    # All checks passed, the image can be labeled by the provider.
    return True
