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
import { addImageToSidePanel } from "./components/sidepanel";
import { eraseAllMarkers, addMarkerWithListener } from "./clickInfoWindow";
import {
  convertGeopointToLatLon,
  getRadius,
  toLatLngLiteral,
  isInVisibleMap,
} from "./utils";
import { DateTime } from "./interface";
import { getGeohashBoxes } from "./geoquery";

let map: google.maps.Map, heatmap: google.maps.visualization.HeatmapLayer;
let selectedLabels: string[] = [];
let selectedDate: DateTime = {};
let timeOfLastRequest: number = Date.now();

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

function initMap() {
  map = new google.maps.Map(document.getElementById("map") as HTMLElement, {
    zoom: 13,
    mapTypeId: "satellite",
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_CENTER,
    },
  });
  getLabelTags();
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
  if (bounds != null) {
    getGeohashBoxes(
      toLatLngLiteral(bounds.getNorthEast()),
      toLatLngLiteral(bounds.getCenter()),
      toLatLngLiteral(bounds.getSouthWest())
    );
  }
  //TODO: check what should be the default radius value.
  const newRadius = getRadius(bounds);
  if (timeOfLastRequest === timeOfRequest) {
    const queriedCollection = queryDB.getQueriedCollection(
      newCenter,
      newRadius,
      selectedLabels,
      selectedDate
    );
    if (timeOfLastRequest === timeOfRequest) {
      //updateNumOfResults(queriedCollection);
      //updateTwentyImagesAndMarkers(queriedCollection);
      queryDB.updateHeatmapFromQuery(heatmap, queriedCollection);
    }
  }
}
async function updateNumOfResults(queriedCollection: firebase.firestore.Query) {
  const numOfResults = (await queriedCollection.get()).docs.length;
  const elementById = document.getElementById("num-of-results");
  if (elementById != null) {
    elementById.innerHTML = numOfResults + " images found";
  }
}

/* Queries for 20 random dataPoints in the database in order to place markers on them. */
//TODO: use this function to show images on the side panel-so they will correlate (relocate to a different file)
/*After any queries change, the images in the side bar should be
updated according to the new queried collection. */
async function updateTwentyImagesAndMarkers(
  queriedCollection: firebase.firestore.Query
): Promise<void> {
  let countOfImagesAndMarkers = 0;
  const elementById = document.getElementById("images-holder");
  eraseAllMarkers();
  let lastVisibleDoc = null;
  let dataRef: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[];
  if (elementById != null) {
    while (countOfImagesAndMarkers < 20) {
      if (lastVisibleDoc == null) {
        dataRef = (await queriedCollection.orderBy("random").limit(20).get())
          .docs;
      } else {
        dataRef = (
          await queriedCollection
            .orderBy("random")
            .startAfter(lastVisibleDoc)
            .limit(20)
            .get()
        ).docs;
      }
      for (let i = 0; i < dataRef.length; i++) {
        const docData = dataRef[i].data();
        if (isInVisibleMap(docData, map)) {
          const imageElement = addImageToSidePanel(docData, elementById);
          await addMarkerWithListener(
            imageElement,
            map,
            convertGeopointToLatLon(docData.coordinates),
            docData.labels,
            selectedDate
          );
          countOfImagesAndMarkers++;
        }
        if (countOfImagesAndMarkers >= 20) {
          break;
        }
      }
      lastVisibleDoc = dataRef[dataRef.length - 1];
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
