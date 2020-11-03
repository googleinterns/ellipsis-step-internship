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

from abc import ABC, abstractmethod

class FilterBy(ABC):
    """ An abstract class for filtering an image by a specific creteria

    """
    def __init__(self, prerequisites):
        self.prerequisites = prerequisites

    @abstractmethod
    def is_supported(self, image_attribute):
        """Checks if the images arribute is supported by the
        provider's prerequisites for a specific criteria.

          Args:
              image_attribute: The image's propery which needs to be checked.

          Returns:
              True iff the image attribute matches the provider's prerequisite.
        """
