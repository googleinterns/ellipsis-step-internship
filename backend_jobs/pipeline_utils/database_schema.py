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
COLLECTION_IMAGES_FIELD_INGESTED_RUNS = 'ingestedRuns'
COLLECTION_IMAGES_FIELD_PROVIDER_ID = 'providerId'
COLLECTION_IMAGES_FIELD_COORDINATES = 'coordinates'
COLLECTION_IMAGES_FIELD_DATE_INGESTED = 'dateIngested'
COLLECTION_IMAGES_FIELD_DATE_SHOT = 'dateShot'
COLLECTION_IMAGES_FIELD_DATE_FIELDS = 'date'
COLLECTION_IMAGES_FIELD_IMAGE_ATTRIBUTES = 'imageAttributes'
COLLECTION_IMAGES_FIELD_FORMAT = 'format'
COLLECTION_IMAGES_FIELD_RESOLUTION = 'resolution'
COLLECTION_IMAGES_FIELD_WIDTH = 'width'
COLLECTION_IMAGES_FIELD_HEIGHT = 'height'
COLLECTION_IMAGES_FIELD_ATTRIBUTION = 'attribution'
# An array of Strings of the labels verftied in the image.
COLLECTION_IMAGES_FIELD_LABELS = 'labels'
COLLECTION_IMAGES_FIELD_RANDOM = 'random'
COLLECTION_IMAGES_FIELD_URL = 'url'
COLLECTION_IMAGES_FIELD_HASHMAP = 'hashmap'
# A VisibilityType member which represents whether the image was verified.
COLLECTION_IMAGES_FIELD_VISIBILITY = 'visibility'

COLLECTION_PIPELINE_RUNS = 'PipelineRuns'
# Constant field names:
# A string of the run's ingestion/recogntion provider's name.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_NAME = 'providerName'
# A string of the run's ingestion/recogntion provider's id.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID = 'providerId'
# A string of the run's ingestion/recogntion provider's version.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VERSION = 'providerVersion'
# A VisibilityType member which represents whether the
# run's provider is enabled/disabled.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VISIBILITY = 'providerVisibility'
# A string of the run's unique id.
COLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID = 'pipelineRunId'
# A Timestamp of the run's start time.
COLLECTION_PIPELINE_RUNS_FIELD_START_DATE = 'startDate'
# A Timestamp of the run's end time.
COLLECTION_PIPELINE_RUNS_FIELD_END_DATE = 'endDate'
# A VisibilityType member which represents whether the
# pipeline run was verified.
COLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY = 'visibility'

COLLECTION_IMAGE_PROVIDERS = 'ImageProviders'
COLLECTION_IMAGE_PROVIDERS_FIELD_PROVIDER_KEYS = 'providerKeys'

COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS = 'PipelineRun'
# Constant field names:
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID = 'providerId'
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_NAME = 'providerName'
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VERSION = 'providerVersion'
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID = 'parentImageId'
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID = 'pipelineRunId'
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_HASHMAP = 'hashmap'
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY = 'visibility'
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM = 'random'

COLLECTION_IMAGES_SUBCOLLECTION_LABELS = 'Labels'
# Constant field names:
# A string of the recognition provider id which recognized the label.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PROVIDER_ID = 'providerId'
# A string of the version of the run's recognition provider.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PROVIDER_VERSION = 'providerVersion'
# A string of the label name as the recognition provider returned.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_NAME = 'labelName'
# An array of Strings of label ids as they are represented in the database.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS = 'labelIds'
# A string of the label doc's parent image id for querying in the
# verifying labels pipeline and the labels removal pipeline.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID = 'parentImageId'
# A string of the unique pipeline run's id
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PIPELINE_RUN_ID = 'pipelineRunId'
# A random number for querying the database by batches.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM = 'random'
# A map of String: String which is used for geographic query.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_HASHMAP = 'hashmap'
# A VisibilityType member which represents whether the label was verified.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_VISIBILITY = 'visibility'

COLLECTION_LABEL_TAGS = 'LabelTags'

COLLECTION_REDEFINE_MAPS = 'RedefineMaps'
# Constant field names:
COLLECTION_REDEFINE_MAPS_FIELD_REDEFINE_MAP = 'redefineMap'
