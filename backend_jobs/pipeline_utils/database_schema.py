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

COLLECTION_IMAGES = 'Images'
# constant fields names:
COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS = 'ingestedProviders'
INGESTED_RUNS = 'ingestedRuns'
PROVIDER_ID = 'providerId'
COORDINATES = 'coordinates'
DATE_INGESTED = 'dateIngested'
DATE_SHOT = 'dateShot'
DATE_FIELDS = 'date'
IMAGE_ATTRIBUTES = 'imageAttributes'
FORMAT = 'format'
RESOLUTION = 'resolution'
WIDTH = 'width'
HEIGHT = 'height'
ATTRIBUTION = 'attribution'
LABELS = 'labels'
RANDOM = 'random'
URL = 'url'
HASHMAP = 'hashmap'

PIPELINE_RUNS_COLLECTION_NAME = 'PipelineRuns'
# Constant field names:
PROVIDER_NAME = 'providerName'
PROVIDER_VERSION = 'providerVersion'
PROVIDER_VISIBILITY = 'providerVisibility'
START_DATE = 'startDate'
END_DATE = 'endDate'

COLLECTION_IMAGES_SUBCOLLECTION_LABELS = 'Labels'
# Constant field names:
LABEL_NAME = 'labelName'
LABEL_IDS = 'labelIds'
PARENT_IMAGE_ID = 'parentImageId'
PIPELINE_RUN_ID = 'pipelineRunId'

LABELTAGS_COLLECTION_NAME = 'LabelTags'

REDEFINE_MAPS_COLLECTION_NAME = 'RedefineMaps'
# Constant field names:
REDEFINE_MAP = 'redefineMap'

# General:
VISIBILITY = 'visibility'
LABEL_VISIBILITY_INVISIBLE  = 0
LABEL_VISIBILITY_VISIBLE  = 1