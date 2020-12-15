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
from backend_jobs.pipeline_utils import database_schema
from backend_jobs.pipeline_utils.data_types import VisibilityType, PipelineRunStatus
from datetime import datetime

_PROJECT_ID_NAME = 'step-project-ellispis'
_PROJECT_ID = 'projectId'


def initialize_db():
    """Initializes project's Firestore database for writing and reading purposes
    and returns a client that can interact with Firestore.

    Returns:
        google.cloud.firestore.Firestore: A `Firestore Client`_.
    """
    # pylint: disable=protected-access
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
            _PROJECT_ID: _PROJECT_ID_NAME,
        })
    return firestore.client()


def store_pipeline_run(provider_id, run_id):
    """ Uploads information about the pipeline run to the
    database_schema.COLLECTION_PIPELINE_RUNS collection
    when pipeline starts.

    """
    db = initialize_db()
    db.collection(database_schema.COLLECTION_PIPELINE_RUNS).document(run_id).set({
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_PROVIDER_ID: provider_id,
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_START_DATE: datetime.now(),
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_VISIBILITY:
            VisibilityType.INVISIBLE.value,
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_PIPELINE_RUN_ID: run_id,
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_STATUS: PipelineRunStatus.STARTED.value
    })

def update_pipeline_run_when_succeeded(run_id):
    """ Updates information about the pipeline run to the
    database_schema.COLLECTION_PIPELINE_RUNS collection relevant document
    when pipeline finishes successfully.

    """
    db = initialize_db()
    doc_ref = db.collection(database_schema.COLLECTION_PIPELINE_RUNS).document(run_id)
    doc_ref.set({
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_END_DATE: datetime.now()
    }, merge=True)
    doc_ref.update({
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_STATUS: PipelineRunStatus.SUCCEEDED.value
    })

def update_pipeline_run_when_failed(run_id):
    """ Updates information about the pipeline run to the
    database_schema.COLLECTION_PIPELINE_RUNS collection relevant document
    when pipeline fails.

    """
    db = initialize_db()
    doc_ref = db.collection(database_schema.COLLECTION_PIPELINE_RUNS).document(run_id)
    doc_ref.update({
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_STATUS: PipelineRunStatus.FAILED.value
    })
