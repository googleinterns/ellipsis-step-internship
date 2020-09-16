/* eslint-disable @typescript-eslint/ban-types */
/*
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types */

import React from "react";
import { DateTime } from "../interface";

/* This component renders information for the info window, in html format.
   @param labels - all the labels this image has, 
   @param url - the image url,
   @param dateTime - the date the image was taken,
   @param attribution - who uplouded the image, */
class InfoWindowContent extends React.Component<{
  labels: string[];
  url: string;
  dateTime: DateTime;
  attribution: string;
}> {
  constructor(props: {
    labels: string[];
    url: string;
    dateTime: DateTime;
    attribution: string;
  }) {
    super(props);
  }

  getLabels() {
    return (
      <>
        <b>Labels: </b>
        {this.props.labels}
      </>
    );
  }

  getImage() {
    return <img className="fit-image" src={this.props.url} />;
  }

  getDate() {
    return (
      <>
        <b>Date: </b>
        {this.props.dateTime.month}/{this.props.dateTime.day}/
        {this.props.dateTime.year}
      </>
    );
  }

  //TODO: add field attribute to database and extract attribute field in this function.
  getAttribution() {
    return (
      <>
        <b>Attribution: </b>
        {"uploader of the image_______"}
      </>
    );
  }

  render(): JSX.Element {
    return (
      <>
        <div className="map-info-window"> {this.getImage()} </div>
        <div>
          <p className="fit-text">
            {this.getLabels()} <br />
            {this.getDate()} <br />
            {this.getAttribution()} <br />
          </p>
        </div>
      </>
    );
  }
}

export default InfoWindowContent;
