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

from imageProviderInterface import ImageProviger
from enums import ProviderType
from imageAttributes import ImageAttributes
import flickrapi

class FlickerProvider(ImageProviger):

    def get_images(self, page):
        flickr = flickrapi.FlickrAPI('2d00397e012c30ccc33ca4fdc05a5c98', 'e36a277c77f09fdd', cache=True)
        photos = flickr.photos.search(text='plasticbag',
                     tag_mode='all',
                     tags='plasticbag',
                     extras='url_c, geo, date_upload, date_taken,original_format, owner_name, original_format',
                     per_page=50,  
                     page=page,
                     sort='relevance')
        return photos[0]

    def get_num_of_batches(self):
        API=FlickerProvider()
        photos= API.get_images(1)
        return (photos.attrib['pages'])

    def get_image_attributes(self,element):
        image_arrributes=ImageAttributes(
            element.get('url_c'),
            ProviderType.satellite,
            element.get('dateupload'),
            element.get('datetaken'),
            [element.get('latitude'),element.get('longitude')],
            element.get('originalformat'),
            element.get('ownername'),
            element.get('height_c'),
            element.get('width_c'))
        return image_arrributes
