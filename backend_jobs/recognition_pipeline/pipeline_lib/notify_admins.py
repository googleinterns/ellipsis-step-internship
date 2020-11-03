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

import smtplib
import ssl

def send_email_to_notify_admins(job_name, ingestion_run = None, ingestion_provider = None):
    """ Sends an email with the pipeline's information to the admin team. 

    The admin team will then know to verify the labels recognized in the current pipeline.
    """

    port = 465  # For SSL
    password = input("Type your password and press enter: ")
    context = ssl.create_default_context()

    sender_email = "verifylabels@gmail.com"
    receiver_email = "ofriavieli@google.com"
    if ingestion_run:
        message = """\
        Subject: New labels to verify

        New images from ingestion run {ingestion_run} were labeled during job {job_name} and are waiting for approval."""\
            .format(ingestion_run = ingestion_run, job_name = job_name)
    else:
        message = """\
        Subject: New labels to verify

        New images from ingestion provider {ingestion_provider} were labeled during job {job_name} and are waiting for approval."""\
            .format(ingestion_provider = ingestion_provider, job_name = job_name)
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("developenta@gmail.com", password)
        server.sendmail(sender_email, receiver_email, message)
