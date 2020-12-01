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
from backend_jobs.ingestion_pipeline.pipeline_lib.image_provider_interface import ImageProvider
from backend_jobs.ingestion_pipeline.pipeline_lib.data_types import ImageType
from backend_jobs.ingestion_pipeline.pipeline_lib.data_types import ImageAttributes
from backend_jobs.ingestion_pipeline.pipeline_lib.firestore_database import get_provider_keys

_PROVIDER_ID = 'FlickrProvider-2020'
_PROVIDER_KEYS = get_provider_keys(_PROVIDER_ID)
_FLICKR_API_KEY = _PROVIDER_KEYS['apiKey']
_FLICKR_SECRET_KEY = _PROVIDER_KEYS['secretKey']
_NUM_OF_IMAGES_PER_PAGE = 100


class FlickrProvider(ImageProvider):
    """ Flickr supports using there urls so we do not need to copy images over.
    Flicker provides metadata as url, resolution,, location etc and does not provide color depth and
    Compression ratio.

    """
    def __init__(self, query_arguments=None):
        self.query_arguments = _parse_query_arguments(query_arguments)

    def get_images(self, page_number):
        photos = self.flickr_api.photos.search(
            # Returns images containing the text in their title, description or tags.
            text=self.query_arguments['text'],
            # Returns images containing the tags listed (multiple tags are delimited by commas).
            tags=self.query_arguments['tags'],
            # 'any' for an OR combination of tags, 'and' for an AND combination of tags.
            tag_mode=self.query_arguments['tag_mode'],
            extras='url_c, geo, date_upload, date_taken, original_format, \
                owner_name, original_format',
            per_page=_NUM_OF_IMAGES_PER_PAGE,
            page=page_number,
            sort='relevance')
        return photos[0]  # return Element 'photos'

    def get_num_of_pages(self):
        photos = self.get_images(1)
        return int(photos.attrib['pages'])

    def get_image_attributes(self, element):
        image_attributes = ImageAttributes(
            url=element.get('url_c'),
            image_id=None,
            image_type=ImageType.CAMERA,
            date_shot=_get_date(element),
            format=element.get('originalformat'),
            attribution=element.get('ownername'),
            latitude=float(element.get('latitude')),
            longitude=float(element.get('longitude')),
            # Extracts width from element, if the width equals str converts to int.
            width_pixels=int(element.get('width_c')) if element.get('width_c') else None,
            # Extracts height from element, if the height equals str converts to int.
            height_pixels=int(element.get('height_c')) if element.get('height_c') else None)
        return image_attributes

    def get_url_for_min_resolution(self,  min_height, min_width, image):
        # This function modifies the url to get the requested resolution,
        # in flickr the resolution is represented in the url.
        # See details at https://www.flickr.com/services/api/misc.urls.html
        url = image['url']
        num_of_underscores = url.count('_')
        max_resolution = min(min_height, min_width)
        # Maping between the char that represents max resolution and the max resolution.
        flickr_resolution_map = {
            75: 's', 100: 't', 150: 'q', 240: 'm', 320: 'n', 400: 'w',
            500: '', 640: 'z', 800: 'c', 1024: 'b', 1600: 'h', 2048: 'k'}
        for key in flickr_resolution_map:
            # Url in the format: https://live.staticflickr.com/{server-id}/{id}_{secret}_{size-suffix}.jpg
            if num_of_underscores == 2:
                if max_resolution <= key:
                    if key == 500:
                        # Removing the char that represents the resolution to get max resolution of 500.
                        return url[:-6] + url[-4:]
                    # Replacing the char that represents the resolution with the wanted key.
                    return url[:-5] + flickr_resolution_map[key] + url[-4:]
            # Url in the format: https://live.staticflickr.com/{server-id}/{id}_{secret}.jpg
            else:
                if max_resolution <= key:
                    if key == 500:
                        # Removing the char that represents the resolution to get max resolution of 500.
                        return url
                    # Adding the char that represents the resolution with the wanted key.
                    return url[:-4] + '_' + flickr_resolution_map[key] + url[-4:]
        raise ValueError('No url with requested resolution')

    flickr_api = flickrapi.FlickrAPI(_FLICKR_API_KEY, _FLICKR_SECRET_KEY, cache=True)
    provider_id = _PROVIDER_ID
    provider_version = '2.4.0'
    enabled = True


def _get_date(element):
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


def _parse_query_arguments(query_arguments):
    """ This function converts a string in the format 'key1:value1-key2:value2' to a dict in the
    format {'key1': 'value1', 'key2': 'value2',...}.

    Args:
        query_arguments: A string cuntianing all the arguments to query by
        e.g. 'tags:cat,plastic-tag_mode:any'.

    Returns:
        A dict of all the args e.g.  {'tags': 'cat,plastic', 'tag_mode': 'any', 'text':''}.
    """
    init_query_arguments = {'tags': 'all', 'tag_mode': 'any', 'text': ''}
    if query_arguments is not None:
        different_arg = query_arguments.split('-')
        for arg in different_arg:
            key = arg.split(':')[0]
            value = arg.split(':')[1]
            if key in init_query_arguments:
                if key == 'tag_mode' and value != 'any' and value != 'all':
                    raise ValueError('Invalid tag_mode, tag_mode can be "any" or "all"')
                init_query_arguments[key] = value
            else:
                raise ValueError('Invalid query_arguments key can be tags, tag_mode or text.')
    return init_query_arguments
