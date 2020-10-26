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
import apache_beam 


class ImageProviger(ABC, apache_beam.DoFn):
    """ 
    Each image provider that is added to the platform will inherit from ImageProvigers class.
    In order to provide images there is a function that returns a list of images,
    and a function that returns the num of batchtes we call the images.
    """

    def get_images(self, element):
        """ 
        This function is incharge of callind an API/Image provider source 
        and recive a list of images 
        Args:
            element: the number of the batch
        Returns: 
            list of images with info on the images.
        """
        pass

    def get_num_of_batches(self):
        """ 
        This function is incharge of calculating the amount of batches we whant to call 
        Returns: 
            num_of_batches: number
        """
        pass

    def get_image_attributes(self):
        """ 
        This function is incharge of exracting the metedata from each image 
        Returns: 
            imageAttributs: ImageAttributs- a class that contains all the info on the image
        """
        pass


    @property
    def provider_id(self):
        raise NotImplementedError
    @property
    def provider_virsion(self):
        raise NotImplementedError
    @property
    def provider_type(self):
        raise NotImplementedError
    @property
    def enabled(self):
        raise NotImplementedError
    @property
    def visibility(self):
        raise NotImplementedError


