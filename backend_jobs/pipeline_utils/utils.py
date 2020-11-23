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

def get_recognition_provider(provider_name, name_to_provider_map):
    """ Returns an object of type ImageRecognitionProvider by the specific provider input.
    If provider is not recognized then throw exception.

    """
    if provider_name in name_to_provider_map:
        return name_to_provider_map[provider_name]
    raise ValueError('{provider} is unknown'.format(provider = provider_name))

def get_provider(name_to_provider_map, provider_name, arguments=None):
    """ Returns an object of type ImageRecognitionProvider by the specific provider input.
    If provider is not recognized then throw exception.

    """
    if provider_name in name_to_provider_map:
        if arguments is not None:
            return name_to_provider_map[provider_name](arguments)
        else:
            return name_to_provider_map[provider_name]()
    raise ValueError('{provider} is unknown'.format(provider = provider_name))

def get_timestamp_id():
    """ Returns a string with only numbers as time id.
    The string will be used as a unique id for each dataflow job.

    """
    return str(datetime.timestamp(datetime.now())).replace('.','')
