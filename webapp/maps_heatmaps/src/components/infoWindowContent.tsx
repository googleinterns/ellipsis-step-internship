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
/* eslint-disable @typescript-eslint/ban-types */

import React from "react";
import { DateTime } from "../interface";

/* This component renders information for the info window, in html format.
   @param labels The labels this image has, 
   @param url The image url,
   @param dateTime The date the image was taken,
   @param attribution The attribution of the image- who uplouded the image, */
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
        {this.props.labels.map((label) => (
          <li key={label}>{label}</li>
        ))}
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

  getAttribution() {
    return (
      <>
        <b>Attribution: </b>
        {this.props.attribution}
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
