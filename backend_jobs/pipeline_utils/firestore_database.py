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
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from backend_jobs.pipeline_utils import constants

def initialize_db():
    """Initializes project's Firestore database for writing and reading purposes.

    """
    # pylint: disable=protected-access
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
        constants.PROJECT_ID: 'step-project-ellispis',
        })
    return firestore.client()

def upload_to_pipeline_runs_collection(provider_id, run_id):
    """ Uploads information about the pipeline run to the Firestore collection

    """
    # pylint: disable=fixme
    # TODO: get start, end and quality of current pipeline run.
    db = initialize_db()
    db.collection(constants.PIPELINE_RUNS_COLLECTION_NAME).document().set({
        constants.PROVIDER_ID: provider_id,
        constants.START_DATE: 00,
        constants.END_DATE: 00,
        constants.VISIBILITY: constants.INVISIBLE,
        constants.PIPELINE_RUN_ID: run_id
    })
