# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM gcr.io/google_appengine/python

RUN apt-get update && apt-get install -y python3-pip curl
RUN pip3 install --upgrade setuptools

# You may later want to change this download as the Cloud SDK version is updated.
RUN curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-322.0.0-linux-x86_64.tar.gz | tar xvz
RUN ./google-cloud-sdk/install.sh -q
RUN ./google-cloud-sdk/bin/gcloud components install beta

ADD . /app/
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
ENV PATH /home/vmagent/app/google-cloud-sdk/bin:$PATH

EXPOSE 8080
WORKDIR /app

CMD gunicorn -b :$PORT main:app
