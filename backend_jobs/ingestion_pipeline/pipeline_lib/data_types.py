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

from datetime import datetime
from dataclasses import dataclass
import enum

class ImageType(enum.Enum):
    """ This enum represents the different imagery types.
    """
    SATELLITE = 1
    DRONE = 2
    LIVE_FEED = 3
    CAMERA = 4

class VisibilityType(enum.Enum):
    """ This enum represents the different visibility types.
    """
    INVISIBLE = 0
    VISIBLE = 1

@dataclass
class ImageAttributes():
    """ This class consists of the attributes we need to extract from each image.
    """
    image_id: str # Unique id of the image.
    url: str # Url of the image, e.g.
    #"https://live.staticflickr.com/3953/15317370767_d01a2327a9_c.jpg"
    image_type: ImageType # Type of image, e.g camera, drone.
    date_shot: datetime # Date the image was taken, e.g. 10/11/14, 5:12 PM
    attribution: str # The attribution of the image, e.g. "Tal Tamir".
    format: str # The format of the image, e.g. "jpg"
    height_pixels: int # Image height resolution, e.g. 500.
    width_pixels: int # Image width resolution, e.g. 500.
    latitude: float # Image latitude coordinate, between -90 and 90.
    longitude: float # Image longitude coordinate, between 80 and 180.
