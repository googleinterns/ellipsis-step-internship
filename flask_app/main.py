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

  A flask app for the project's admins for running all backend pipelines.

  The app includes a page for each pipeline with it's specific arguments and
  a log of recent pipeline runs of all different pipelines and statuses.
 """
from threading import Thread
from flask import Flask, request, render_template
from firebase_admin import firestore
from backend_jobs.recognition_pipeline.main import run as run_recognition_pipeline
from backend_jobs.ingestion_pipeline.main import run as run_ingestion_pipeline
from backend_jobs.recognition_removal.main import run as run_recognition_removal
from backend_jobs.ingestion_removal.main import run as run_ingestion_removal
from backend_jobs.verify_labels.main import run as run_recognition_verification
from backend_jobs.ingestion_update_visibility.main import run as run_ingestion_verification

from backend_jobs.pipeline_utils.firestore_database import initialize_db
from backend_jobs.pipeline_utils import database_schema


app = Flask(__name__)

_INPUT_TYPE_PROVIDER = 'provider'
_INPUT_TYPE_RUN_ID = 'run-id'
_TEST_OUTPUT = 'outputs'
_RUN_LOCALLY = False
_NUM_OF_LATEST_RUNS = 10


def get_latest_runs(status):
    """ This function given a status returns a limted list of pipeline run documents.

    Args:
        status- The status of the pipeline runs we want to receive.

    Returns:
        List of pipeline run documents, each document is presented as a dict.
    """
    db = initialize_db()
    query = db.collection(database_schema.COLLECTION_PIPELINE_RUNS)\
        .where(database_schema.COLLECTION_PIPELINE_RUNS_FIELD_STATUS, u'==', status)\
        .order_by(
            database_schema.COLLECTION_PIPELINE_RUNS_FIELD_START_DATE,
            direction=firestore.Query.DESCENDING)\
        .limit(_NUM_OF_LATEST_RUNS).stream()
    return [doc.to_dict() for doc in query]


def run_pipeline(target, kwargs):
    thread = Thread(target=target, kwargs=kwargs)
    thread.start()
    return all_pipelines_page()


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/recognition')
def recognition_page():
    return render_template('recognition.html')


@app.route('/ingestion')
def ingestion_page():
    return render_template('ingestion.html')


@app.route('/all_pipelines', methods=['GET'])
def all_pipelines_page():
    return render_template('all_pipelines.html')


@app.route('/ingestion_verification')
def ingestion_verification_page():
    return render_template('ingestion_verification.html')


@app.route('/recognition_verification')
def recognition_verification_page():
    return render_template('recognition_verification.html')


@app.route('/ingestion_removal')
def ingestion_removal_page():
    return render_template('ingestion_removal.html')


@app.route('/recognition_removal')
def recognition_removal_page():
    return render_template('recognition_removal.html')


@app.route('/submit_all_pipeline', methods=['POST'])
def submit_all_pipelines_page():
    """ Presents all latest pipeline runs logs of the requested status.
    The status can be either STARTED, SUCCEEDED or FAILED
    """
    status_type = request.form['status_type']
    my_objects = get_latest_runs(status_type)
    return render_template('all_pipelines.html', my_objects=my_objects)


@app.route('/submit_recognition', methods=['POST'])
def submit_recognition():
    """ This function creates a thread to run the recognition pipeline.
    """
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    input_recognition_provider = request.form['recognition_provider']
    target = run_recognition_pipeline
    kwargs = {
        'recognition_provider_name': input_recognition_provider,
        'output_name': _TEST_OUTPUT,
        'run_locally': _RUN_LOCALLY}
    if input_type == _INPUT_TYPE_PROVIDER:
        kwargs['ingestion_provider'] = input_value
    else:
        kwargs['ingestion_run'] = input_value
    return run_pipeline(target, kwargs)


@app.route('/submit_ingestion', methods=['POST'])
def submit_ingestion():
    """ This function creates a thread to run the ingestion pipeline.
    """
    input_value = request.form['input_value']
    input_provider_args = request.form['arguments']
    target = run_ingestion_pipeline
    kwargs = {
        'input_provider_name': input_value,
        'input_provider_args': input_provider_args,
        'output_name': _TEST_OUTPUT,
        'run_locally': _RUN_LOCALLY}
    return run_pipeline(target, kwargs)


@app.route('/submit_recognition_verification', methods=['POST'])
def submit_recognition_verification():
    """ This function creates a thread to run the recognition verification pipeline.
    """
    input_value = request.form['input_value']
    target = run_recognition_verification
    kwargs = {
        'recognition_run': input_value,
        'output': _TEST_OUTPUT,
        'run_locally': _RUN_LOCALLY}
    return run_pipeline(target, kwargs)


@app.route('/submit_ingestion_verification', methods=['POST'])
def submit_ingestion_verification():
    """ This function creates a thread to run the ingestion verification pipeline.
    """
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    input_visibility = request.form['visibility_type']
    target = run_ingestion_verification
    kwargs = {'input_visibility': input_visibility, 'run_locally': _RUN_LOCALLY}
    if input_type == _INPUT_TYPE_PROVIDER:
        kwargs['input_image_provider'] = input_value
    else:
        kwargs['input_pipeline_run'] = input_value
    return run_pipeline(target, kwargs)


@app.route('/submit_recognition_removal', methods=['POST'])
def submit_recognition_removal():
    """ This function creates a thread to run the recognition removal pipeline.
    """
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    target = run_recognition_removal
    kwargs = {'output': _TEST_OUTPUT, 'run_locally': _RUN_LOCALLY}
    if input_type == _INPUT_TYPE_PROVIDER:
        kwargs['recognition_provider'] = input_value
    else:
        kwargs['recognition_run'] = input_value
    return run_pipeline(target, kwargs)


@app.route('/submit_ingestion_removal', methods=['POST'])
def submit_ingestion_removal():
    """ This function creates a thread to run the ingestion removal pipeline.
    """
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    target = run_ingestion_removal
    kwargs = {'run_locally': _RUN_LOCALLY}
    if input_type == _INPUT_TYPE_PROVIDER:
        kwargs['input_image_provider'] = input_value
    else:
        kwargs['input_pipeline_run'] = input_value
    return run_pipeline(target, kwargs)


if __name__ == '__main__':
    app.run(debug=True)
