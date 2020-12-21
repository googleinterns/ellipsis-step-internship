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
# Type: array of strings, saves all providers that ingested this image.
COLLECTION_IMAGES_FIELD_INGESTED_PROVIDERS = 'ingestedProviders'
# Type: array of strings, saves all pipelineruns that ingested this image.
COLLECTION_IMAGES_FIELD_INGESTED_RUNS = 'ingestedRuns'
# Type: string, unique id of the provider.
COLLECTION_IMAGES_FIELD_PROVIDER_ID = 'providerId'
# Type: geopoint, location of the image.
COLLECTION_IMAGES_FIELD_COORDINATES = 'coordinates'
# Type: timestamp, the date the image was ingested.
COLLECTION_IMAGES_FIELD_DATE_INGESTED = 'dateIngested'
# Type: timestamp, the date the image shot was taken.
COLLECTION_IMAGES_FIELD_DATE_SHOT = 'dateShot'
# Type: map of numbers, the date the image was ingested.
#  e.g.{'year': year, 'month': month, 'day': day}
COLLECTION_IMAGES_FIELD_DATE_FIELDS = 'date'
# Type: map, saves all of the image attributes, e.g. format and resolution.
COLLECTION_IMAGES_FIELD_IMAGE_ATTRIBUTES = 'imageAttributes'
# Type: string, image type, e.g. 'jpg'.
COLLECTION_IMAGES_FIELD_FORMAT = 'format'
# Type: map, image resultion containing width and height.
COLLECTION_IMAGES_FIELD_RESOLUTION = 'resolution'
# Type: number, the width of the image.
COLLECTION_IMAGES_FIELD_WIDTH = 'width'
# Type: number, the height of the image.
COLLECTION_IMAGES_FIELD_HEIGHT = 'height'
# Type: string, the attribution of the image (the persion how took the shot of the image).
COLLECTION_IMAGES_FIELD_ATTRIBUTION = 'attribution'
# Type: array of Strings, the labels verified in the image.
COLLECTION_IMAGES_FIELD_LABELS = 'labels'
# Type: number, a random number for querying the database by batches.
COLLECTION_IMAGES_FIELD_RANDOM = 'random'
# Type: string, the url of the image.
COLLECTION_IMAGES_FIELD_URL = 'url'
# Type: map of String, string which is used for geographic query.
COLLECTION_IMAGES_FIELD_HASHMAP = 'hashmap'
# Type: member, A VisibilityType member which represents whether the image was verified.
COLLECTION_IMAGES_FIELD_VISIBILITY = 'visibility'


COLLECTION_PIPELINE_RUNS = 'PipelineRuns'
# Constant field names:
# Type: string, the run's ingestion/recogntion provider's name.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_NAME = 'providerName'
# Type: string, the run's ingestion/recogntion provider's id.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID = 'providerId'
# Type: string, the run's ingestion/recogntion provider's version.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VERSION = 'providerVersion'
# Type: number, a VisibilityType which represents whether the
# run's provider is enabled/disabled.
COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VISIBILITY = 'providerVisibility'
# Type: string, the run's unique id.
COLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID = 'pipelineRunId'
# Type: timestamp, the run's start time.
COLLECTION_PIPELINE_RUNS_FIELD_START_DATE = 'startDate'
# Type: Timestamp, the run's end time.
COLLECTION_PIPELINE_RUNS_FIELD_END_DATE = 'endDate'
# Type: number, a VisibilityType which represents whether the
# pipeline run was verified.
COLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY = 'visibility'

COLLECTION_IMAGE_PROVIDERS = 'ImageProviders'
COLLECTION_IMAGE_PROVIDERS_FIELD_PROVIDER_KEYS = 'providerKeys'

COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS = 'PipelineRun'
# Constant field names:
# Type: string, the ingestion provider id.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID = 'providerId'
# Type: string, the ingestion provider Name.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_NAME = 'providerName'
# Type: string, the ingestion provider viesion.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_VERSION = 'providerVersion'
# Type: string, the pipelineRun doc's parent image id for querying in the removal pipeline.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PARENT_IMAGE_ID = 'parentImageId'
# Type: string, the unique pipeline run's id.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID = 'pipelineRunId'
# Type: map of String, string which is used for geographic query.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_HASHMAP = 'hashmap'
# Type: number, a VisibilityType which represents whether the image was verified.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY = 'visibility'
# Type: number, a random number for querying the database by batches.
COLLECTION_IMAGES_SUBCOLLECTION_PIPELINE_RUNS_FIELD_RANDOM = 'random'

COLLECTION_IMAGES_SUBCOLLECTION_LABELS = 'Labels'
# Constant field names:
# Type: string, the recognition provider id which recognized the label.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PROVIDER_ID = 'providerId'
# Type: string, the version of the run's recognition provider.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PROVIDER_VERSION = 'providerVersion'
# Type: string, the label name as the recognition provider returned.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_NAME = 'labelName'
# Type: array of Strings, presents all the label ids as they are represented in
# the database.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_IDS = 'labelIds'
# Type: string, the label doc's parent image id for querying in the
# verifying labels pipeline and the labels removal pipeline.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PARENT_IMAGE_ID = 'parentImageId'
# Type: string, the unique pipeline run's id
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_PIPELINE_RUN_ID = 'pipelineRunId'
# Type: number, a random number for querying the database by batches.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_RANDOM = 'random'
# Type: map of String, a string which is used for geographic query.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_HASHMAP = 'hashmap'
# Type: number, a VisibilityType which represents whether the label was verified.
COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_VISIBILITY = 'visibility'

COLLECTION_LABEL_TAGS = 'LabelTags'

COLLECTION_REDEFINE_MAPS = 'RedefineMaps'
# Constant field names:
# Type: map of String, string which maps label names to label ids
# for the verifying labels pipeline.
COLLECTION_REDEFINE_MAPS_FIELD_REDEFINE_MAP = 'redefineMap'

COLLECTION_HEATMAP = 'Heatmap'

COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS = 'WeightedPoints'
# Constant field names:
# Type: string, the unique label id.
COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_LABEL_ID = 'labelId'
# Type: geopoint, quantized coordinates.
COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_QUANTIZED_COORDINATES =\
  'quantizedCoordinates'
# Type: number, counts the number images represented by this point.
COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_WEIGHT = 'weight'
# Type: map of String, a string which is used for geographic query.
COLLECTION_HEATMAP_SUBCOLLECTION_WEIGHTED_POINTS_FIELD_HASHMAP = 'hashmap'
