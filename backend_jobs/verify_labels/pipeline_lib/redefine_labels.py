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

import apache_beam as beam
from backend_jobs.pipeline_utils.firestore_database import initialize_db
from backend_jobs.pipeline_utils import database_schema

def get_redefine_map(recognition_provider_id):
    """ Returns the recognition ptovider's specific redefine labels map
        as stroed in the COLLECTION_REDEFINE_MAPS.

    """
    db = initialize_db()
    doc_dict = db.collection(database_schema.COLLECTION_REDEFINE_MAPS).\
        document(recognition_provider_id).get().to_dict()
    return doc_dict[database_schema.COLLECTION_REDEFINE_MAPS_FIELD_REDEFINE_MAP]

# pylint: disable=abstract-method
class RedefineLabels(beam.DoFn):
    """Converts parallelly the labels returned from
    the provider to the corresponding label Id's.

    Input:
       Python dictionary containing all the fields of the document in the
       database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS and their values.

    Output:
       A generator of tuples of dictionary of label documents' properties (same as input)
       and list of label ids.

    """

    # pylint: disable=arguments-differ
    def process(self, element, redefine_map):
        """Uses the global redefine map to map the different labels to the project's label Ids.

        Args:
            element: Python dictionary of label properties.
            redefine_map: a specific provider's redefine map from the database.

        Yields:
            (dictionary of label doc properties, label ids list)
        """
        label_name =\
            element[database_schema.COLLECTION_IMAGES_SUBCOLLECTION_LABELS_FIELD_LABEL_NAME]
        if label_name in redefine_map:
            yield (element, redefine_map[label_name])
