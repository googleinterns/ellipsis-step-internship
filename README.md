# Platform to analyze images and map objects

This repository contains the code for the
[STEP internship](https://buildyourfuture.withgoogle.com/programs/step/)
on mapping plastic waste based on crawling web images.

__Disclaimer__: This is not an officially supported Google product.

## Source Code Headers

Every file containing source code must include copyright and license
information. This includes any JS/CSS files that you might be serving out to
browsers. (This is to help well-intentioned people avoid accidental copying that
doesn't comply with the license.)

Apache header:

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


## Instructions

#### Setup:
1. Create google cloud account
2. Activate:
    * Firebase
    * Dataflow
    * App engine
    * A storage bucket
3. Installing the google cloud CLI- https://cloud.google.com/sdk/docs/install
4. Clone this repo: `git clone https://github.com/googleinterns/ellipsis-step-internship`
5. Go to the right directory- `cd  ellipsis-step-internship`

#### Backend run locally-
1. Go to the right directory- `cd flask_app`
2. Run:  
    `export FLASK_APP=main.py`  
    `flask run --host=0.0.0.0`

#### Backend deploy-
1. Go to the right directory- `cd flask_app`
2. Deploy the user interface - `gcloud app deploy`
3. View your application- `gcloud app browse`
4. Stream logs from the command line - `gcloud app logs tail -s default`

#### Frontend run locally-
1. Go to the right directory- `cd webapp/maps_heatmaps/src`
2. Set the API Key  
    `export GOOGLE_MAPS_API_KEY=SECRET_KEY`  
    `export FIRESTORE_API_KEY=SECRET_KEY`  
    To find the SECRET_KEY go to:  
    * Your google cloud account
    * APIs & Services
    * Credentials
3. Install the node modules- `npm install`
4. Run the dev server - `npm run dev`
5. Then, go to localhost:8080


#### Frontend deploy-
1. Install the Firebase CLI- https://firebase.google.com/docs/cli#install_the_firebase_cli
2. Go to the right directory- `cd webapp/maps_heatmaps/src`
3. Initialize your project - `firebase init hosting`
4. Build the site - `npm run build`
5. Deploy to your site - `firebase deploy --only hosting`

Resources for getting more info:
* https://firebase.google.com/docs/hosting/quickstart
* https://firebase.google.com/docs/hosting/deploying












