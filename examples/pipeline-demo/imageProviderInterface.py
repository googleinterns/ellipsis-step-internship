from abc import ABC, abstractmethod 
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

import apache_beam 


class ImageProviger(ABC, apache_beam.DoFn):
    """
    Each image provider that is added to the platform will inherit from ImageProvigers class.
    In order to provide images there is a function that returns a list of images,
    and a function that returns the num of batchtes we call the images.
    """
    @property
    def image_type(self):
        pass

    def get_images(self, element):
        pass

    def get_num_of_batches(self):
        pass

    def get_image_attributes(self):
        """ This function is incharge of exracting the metedata for each image 
        return type- imageAttributs
        """
        pass


'''
class ExtractInformation(ABC, apache_beam.DoFn):

    def get_image_attributes(self):
        """ This function is incharge of exracting the metedata for each image 
        return type- imageAttributs
        """
        pass

    def get_url(self):
        pass
    def get_provider_type(self):
        pass
    def get_date_upload(self):
        pass
    def get_date_taken(self):
        pass
    def get_location(self):
        pass
    def get_resolution(self):
        pass
    def get_compression_ratio(self):
        pass
    def get_format(self):
        pass
    def get_color_depth(self):
        pass
'''