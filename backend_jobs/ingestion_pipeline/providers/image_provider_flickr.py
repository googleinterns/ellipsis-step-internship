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
import flickrapi
from backend_jobs.ingestion_pipeline.pipeline_lib.firestore_database import get_doc_by_id
from backend_jobs.ingestion_pipeline.pipeline_lib.image_provider_interface import ImageProvider
from backend_jobs.ingestion_pipeline.pipeline_lib.data_types import ImageType
from backend_jobs.ingestion_pipeline.pipeline_lib.data_types import VisibilityType
from backend_jobs.ingestion_pipeline.pipeline_lib.data_types import ImageAttributes

_FLICKR_API_KEY = '2d00397e012c30ccc33ca4fdc05a5c98'
_FLICKR_SECRET_KEY =  'e36a277c77f09fdd'

class FlickrProvider(ImageProvider):
    """ This class is an implementation for the ImageProvider interface.
    """
    def get_images(self, num_of_page, query_arguments):
        flickr = flickrapi.FlickrAPI(_FLICKR_API_KEY, _FLICKR_SECRET_KEY, cache = True)
        photos = flickr.photos.search(text=query_arguments['tag'],
                     tag_mode = 'all',
                     tags = query_arguments['tag'],
                     extras = 'url_c, geo, date_upload, date_taken, original_format,\
                      owner_name, original_format',
                     per_page = self.num_of_images,
                     page = num_of_page,
                     sort = 'relevance')
        return photos[0]

    def get_num_of_pages(self, query_arguments):
        photos = self.get_images(1, query_arguments)
        return int(photos.attrib['pages'])

    def get_image_attributes(self, element):
        image_arrributes=ImageAttributes(
            url = element.get('url_c'),
            image_id = self._genarate_image_id_with_prefix(element.get('id')),
            image_type = ImageType.CAMERA,
            date_shot = get_date(element),
            coordinates = get_coordinates(element),
            format = element.get('originalformat'),
            attribution = element.get('ownername'),
            resolution = get_resolution(element))
        return image_arrributes

    def get_url_for_max_resolution(self, resolution, image_id):
        doc = get_doc_by_id(image_id)
        if doc.exists:
            url = doc.to_dict()[u'url']
            max_resolution =  max(resolution['height'],resolution['width'])
            flickr_resolution_map = {75:'s',100:'t',150	:'q',240:'m',320:'n',400:'w',
            500:'',640:'z',800:'c',1024:'b',1600:'n',2048:'k'}
            for key in flickr_resolution_map:
                if  max_resolution <= key:
                    if key == 500:
                        return url[:-6] + url[-4:]
                    return url[:-5] + flickr_resolution_map[key] + url[-4:]
        return None

    def parse_query_by_args(self, args):
        if args is not None:
            return {'tag': args}
        return {'tag': 'all'}

    def _genarate_image_id_with_prefix(self, image_id):
        return str(self.provider_id + image_id)

    provider_id = 'FlickrProvider-2020'
    provider_name ='FlickrProvider'
    provider_version = '2.4.0'
    image_type = ImageType.CAMERA
    enabled = True
    visibility = VisibilityType.NOBODY
    num_of_images = 100

def get_coordinates(element):
    """ This function extracts coordinates from the image element,
    if the coordinates equals (0,0) the function returns None.

    Args:
        element: A dict cuntianing all the image attributes.

    Returns:
        Coordinates in the format {'latitude':float,'longitude':float}.
    """
    latitude=float(element.get('latitude'))
    longitude=float(element.get('longitude'))
    if (latitude==0.0 and longitude==0.0):
        coordinates=None
    else:
        coordinates={'latitude':latitude,'longitude':longitude}
    return coordinates

def get_resolution(element):
    """ This function extracts resolution from the image element,
    if the resolution equals None the function returns None.

    Args:
        element: A dict cuntianing all the image attributes.

    Returns:
        Resolution in the format {'height':int,'width':int}.
    """
    height=element.get('height_c')
    width=element.get('width_c')
    if (height is None and width is None):
        resolution=None
    else:
        resolution={'height':int(height),'width':int(width)}
    return resolution

def get_date(element):
    """ This function extracts the date the image was taken from the image element
    and converts it to a datetime format.

    Args:
        element: A dict cuntianing all the image attributes.

    Returns:
        Date the image was taken in the format of datatime.
    """
    date_taken = element.get('datetaken')
    datetime_date_taken = datetime.strptime(date_taken, '%Y-%m-%d %H:%M:%S')
    return datetime_date_taken
