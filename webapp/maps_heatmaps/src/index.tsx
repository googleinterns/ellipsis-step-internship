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

// [START maps_layer_heatmap]
// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">

// Imports
import * as firebase from "firebase";
import * as geofirestore from "geofirestore";
import { database } from "./declareDatabase";
import * as queryDB from "./queryDB";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React from "react";
import ReactDOM from "react-dom";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import SidePanel from "./components/sidepanel";
import {
  eraseAllMarkers,
  convertGeopointToLatLon,
  addMarkerWithListener,
} from "./clickInfoWindow";
import { DateTime } from "./interface";

let map: google.maps.Map, heatmap: google.maps.visualization.HeatmapLayer;
let selectedLabels: string[] = [];
let selectedDate: DateTime = {};
let timeOfLastRequest: number = Date.now();
getLabelTags();

/*Gets all the different labels from the label Collection in firestore data base
 and adds them as options for label querying."*/
async function getLabelTags() {
  const labelsRef = (await database.collection("LabelTags").get()).docs;
  const labelTags: Array<{ value: string; label: string }> = [];
  labelsRef.forEach((doc) => {
    const name = doc.data().name;
    labelTags.push({ value: name, label: name });
  });
  ReactDOM.render(
    <SidePanel labels={labelTags} />,
    document.querySelector("#root")
  );
  selectedLabels = labelTags.map((x: Record<string, string>) => x.label);
}

async function initMap() {
  map = new google.maps.Map(document.getElementById("map") as HTMLElement, {
    zoom: 13,
    mapTypeId: "satellite",
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_CENTER,
    },
  });

  // TODO: decide where to set default center.
  const images = database.collection("images");
  images.get().then((querySnapshot) => {
    if (!querySnapshot.empty) {
      const image = querySnapshot.docs[0].data();
      map.setCenter({
        lat: image.coordinates.latitude,
        lng: image.coordinates.longitude,
      });
    }
  });

  heatmap = new google.maps.visualization.HeatmapLayer({
    data: [],
    map: map,
  });
  map.addListener("center_changed", () => mapChanged());
  map.addListener("zoom_changed", () => mapChanged());
}
/* Updates the map and the sidepanel after any change of the
center/zoom of the current map or of the different queries.*/
async function mapChanged() {
  const timeOfRequest = Date.now();
  timeOfLastRequest = timeOfRequest;
  const center: google.maps.LatLng = map.getCenter();
  const lat = center.lat();
  const lng = center.lng();
  const newCenter = new firebase.firestore.GeoPoint(lat, lng);
  const bounds = map.getBounds(); //map's current bounderies
  //TODO: check what should be the default radius value.
  let newRadius = 2;
  if (bounds) {
    const meterRadius = google.maps.geometry.spherical.computeDistanceBetween(
      bounds.getCenter(),
      bounds.getNorthEast()
    );
    newRadius = meterRadius * 0.000621371192; //convert to miles
  }
  if (timeOfLastRequest === timeOfRequest) {
    const queriedCollection = queryDB.getQueriedCollection(
      newCenter,
      newRadius,
      selectedLabels,
      selectedDate
    );
    if (timeOfLastRequest === timeOfRequest) {
      updateNumOfResults(queriedCollection);
      updateTwentyImages(queriedCollection);
      queryDB.updateHeatmapFromQuery(heatmap, queriedCollection);
    }
  }
}
async function updateNumOfResults(queriedCollection: geofirestore.GeoQuery) {
  const numOfResults = (await queriedCollection.get()).docs.length;
  const elementById = document.getElementById("num-of-results");
  if (elementById != null) {
    elementById.innerHTML = numOfResults + " images found";
  }
}
/*After any queries change, the images in the side bar should be
updated according to the new queried collection. */
async function updateTwentyImages(
  queriedCollection: geofirestore.GeoQuery
): Promise<void> {
  const dataRef = (await queriedCollection.get()).docs;
  const jump = Math.ceil(dataRef.length / 10);
  const elementById = document.getElementById("images-holder");
  if (elementById != null) {
    eraseAllMarkers();
    elementById.innerHTML = "";
    for (let i = 0; i < dataRef.length; i = i + jump) {
      const docData = dataRef[i].data();
      const imageElement = document.createElement("img");
      imageElement.className = "sidepanel-image";
      imageElement.src = docData.url;
      elementById.appendChild(imageElement);
      await addMarkerWithListener(
        imageElement,
        map,
        convertGeopointToLatLon(docData.g.geopoint),
        docData.labels,
        selectedDate
      );
    }
  }
}
/* Updates the global queries variables according to 
the client's inputs on the side panel. 
Changes the map according to the new variables. */
function queriesChanged(selectedQueries: {
  labels: string[];
  year: number | undefined;
  month: number | undefined;
}): void {
  selectedLabels = selectedQueries.labels;
  selectedDate = { year: selectedQueries.year, month: selectedQueries.month };
  mapChanged();
}
// [END maps_layer_heatmap]

export { initMap, database, queriesChanged, map };