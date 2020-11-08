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

class ProviderType(enum.Enum):
    """
    This enum represents the different imagery types
    """
    satellite = 1
    drone = 2
    live_feed = 3
    camera = 4


class VisibilityType (enum.Enum):
    """
    This enum represents the different visibility types
    """
    everyone = 1
    developerOnly = 2
    nobody = 3


@dataclass
class ImageAttributes():
    """
    This class consists of the attributes we need to extracy from each image.
    """
    id: str
    url: str
    provider_type: ProviderType
    date_shot: datetime
    location:list
    attribution:str
    format:str
    resolution: {}
    #TODO: add compression_ratio:str and color_depth:str
