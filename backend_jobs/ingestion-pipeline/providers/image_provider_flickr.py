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


from pipeline_lib.image_provider_interface import ImageProvider
from pipeline_lib.additional_classes import ProviderType
from pipeline_lib.additional_classes import VisibilityType
from pipeline_lib.additional_classes import ImageAttributes
import flickrapi


class FlickrProvider(ImageProvider):
    """
    This class is an implementation for the ImageProvider interface.
    """
    def get_images(self, num_of_batches, num_of_images, query_arguments):
        flickr = flickrapi.FlickrAPI(
            '2d00397e012c30ccc33ca4fdc05a5c98',
            'e36a277c77f09fdd',
            cache=True)
        photos = flickr.photos.search(text=query_arguments['tag'],
                     tag_mode = 'all',
                     tags = query_arguments['tag'],
                     extras = 'url_c, geo, date_upload, date_taken, original_format,\
                      owner_name, original_format',
                     per_page = num_of_images,
                     page = num_of_batches,
                     sort = 'relevance')
        return photos[0]

    def get_num_of_batches(self,query_arguments):
        photos = self.get_images(1, self.num_of_images,query_arguments)
        print(photos.attrib)
        return photos.attrib['pages']

    def get_image_attributes(self, element):
        image_arrributes=ImageAttributes(
            url = element.get('url_c'),
            id =self.provider_name + element.get('id'),
            provider_type = ProviderType.camera,
            date_upload=element.get('dateupload'),
            date_taken=element.get('datetaken'),
            location=get_location(element),
            format=element.get('originalformat'),
            attribution=element.get('ownername'),
            resolution=get_resolution(element))
        return image_arrributes

    provider_id = 'flickr_2020'
    provider_name ='flickr'
    provider_version = '2.4.0'
    provider_type = ProviderType.camera
    enabled = True
    visibility = VisibilityType.developerOnly
    num_of_images =100

def get_location(element):
    """
    This function gets location from metadata and if location eql (0,0) returns None.
    """
    latitude=float(element.get('latitude'))
    longitude=float(element.get('longitude'))
    if (latitude==0.0 and longitude==0.0):
        location=None
    else:
        location=[latitude,longitude]
    return location

def get_resolution(element):
    """
    This function gets location from metadata and if location eql (0,0) returns None.
    """
    height=element.get('height_c')
    width=element.get('width_c')
    if (height is None and width is None):
        resolution=None
    else:
        resolution={'height':int(height),'width':int(width)}
    return resolution
