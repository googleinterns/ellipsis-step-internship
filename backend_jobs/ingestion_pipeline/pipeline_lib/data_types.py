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
    """
    This enum represents the different imagery types.
    """
    SATELLITE = 1
    DRONE = 2
    LIVE_FEED = 3
    CAMERA = 4


class VisibilityType (enum.Enum):
    """
    This enum represents the different visibility types
    """
    NOBODY = 1
    EVERYONE = 2


@dataclass
class ImageAttributes():
    """ This class consists of the attributes we need to extract from each image.
    """
    image_id: str
    url: str
    image_type: ImageType
    date_shot: datetime
    attribution: str
    format: str
    resolution: {} # type {'height':int, 'width':int}
    coordinates: {} # type {'latitude':float, 'longitude':float}
