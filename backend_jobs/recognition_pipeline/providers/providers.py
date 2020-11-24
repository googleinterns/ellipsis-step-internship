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

from backend_jobs.recognition_pipeline.providers import google_vision_api

# Maps recognition provider names to an object of the provider.
_NAME_TO_PROVIDER = {'Google_Vision_API': google_vision_api.GoogleVisionAPI()}

def get_recognition_provider(provider_name):
    """ Returns an object of type ImageRecognitionProvider by the specific provider input.
    If provider is not recognized then throw exception.

    """
    if provider_name in _NAME_TO_PROVIDER:
        return _NAME_TO_PROVIDER[provider_name]
    raise ValueError('{provider} is unknown'.format(provider = provider_name))
