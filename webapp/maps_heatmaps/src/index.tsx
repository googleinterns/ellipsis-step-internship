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
import { addImageToSidePanel, updateNumOfResults } from "./sidepanelUtils";
import { eraseAllMarkers, addMarkerWithListener } from "./clickInfoWindow";
import {
  convertGeopointToLatLon,
  getRadius,
  toLatLngLiteral,
  isInVisibleMap,
} from "./utils";
import { DateTime } from "./interface";
import { getGeohashBoxes } from "./geoquery";
import { hash, decodeHash } from "geokit";

let map: google.maps.Map, heatmap: google.maps.visualization.HeatmapLayer;
let selectedLabels: string[] = [];
let selectedDate: DateTime = {};
let timeOfLastRequest: number = Date.now();
let queriedCollections: firebase.firestore.Query[];
let lastVisibleDocs: firebase.firestore.QueryDocumentSnapshot<
  firebase.firestore.DocumentData
>[];
const numOfImagesAndMarkers = 20;

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
  const bounds = map.getBounds(); //map's current bounderies
  if (bounds != null) {
    const arrayhash = getGeohashBoxes(
      toLatLngLiteral(bounds.getNorthEast()),
      toLatLngLiteral(bounds.getCenter()),
      toLatLngLiteral(bounds.getSouthWest())
    );
    if (timeOfLastRequest === timeOfRequest) {
      eraseAllMarkers();
      queriedCollections = [];
      lastVisibleDocs = [];
      arrayhash.forEach((hash: string) => {
        const queriedCollection = queryDB.getQueriedCollection(
          hash,
          selectedLabels,
          selectedDate
        );
        if (timeOfLastRequest === timeOfRequest) {
          queriedCollections.push(queriedCollection);
        }
      });
      await queryDB.updateHeatmapFromQuery(heatmap, queriedCollections);
      updateNumOfResults(queriedCollections);
      updateImagesAndMarkers(true);
    }
  }
}

//TODO: Check if its is better to get less than 20 docs each time.
async function getNextDocs(index: number, first: boolean) {
  let docsArray: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[];
  if (first) {
    docsArray = (
      await queriedCollections[index].limit(numOfImagesAndMarkers).get()
    ).docs;
    console.log("first");
    first = false;
  } else {
    docsArray = (
      await queriedCollections[index]
        .startAfter(lastVisibleDocs[index])
        .limit(20)
        .get()
    ).docs;
  }
  return docsArray;
}

/* Queries for 20 random dataPoints in the database in order to place markers on them. 
After any queries change, the images in the side bar should be
updated according to the new queried collection. */
async function updateImagesAndMarkers(first: boolean): Promise<void> {
  let countOfImagesAndMarkers = 0;
  const elementById = document.getElementById("images-holder");
  let dataRef: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[];
  const allDocArrays: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[][] = new Array<
    firebase.firestore.QueryDocumentSnapshot<firebase.firestore.DocumentData>[]
  >(queriedCollections.length);
  const pointers: number[] = new Array<number>(queriedCollections.length);
  for (let i = 0; i < queriedCollections.length; i++) {
    allDocArrays[i] = await getNextDocs(i, true);
    pointers[i] = 0;
  }
  if (elementById != null) {
    elementById.innerHTML = "";
    while (countOfImagesAndMarkers < 20) {
      const minDocData = await getDataOfMinDoc(allDocArrays, pointers);
      const latlng = convertGeopointToLatLon(minDocData.coordinates);
      const imageElement = addImageToSidePanel(minDocData, elementById);
      await addMarkerWithListener(
        imageElement,
        map,
        latlng,
        hash({ lat: latlng.lat(), lng: latlng.lng() }, 10),
        minDocData.labels,
        selectedDate
      );
      countOfImagesAndMarkers++;
    }
  }
}

//TODO: Figure out how not to give priority to the doc in the first geohash
async function getDataOfMinDoc(
  allDocArrays: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[][],
  pointers: number[]
) {
  let minDoc = allDocArrays[0][pointers[0]];
  let indexOfMin = 0;
  for (let i = 1; i < allDocArrays.length; i++) {
    const pointer = pointers[i];
    const doc = allDocArrays[0][pointer];
    if (doc.data().random < minDoc.data().random) {
      minDoc = doc;
      indexOfMin = i;
    }
  }
  pointers[indexOfMin]++;
  /* Done with all docs of this geohash, need to get next ones. */
  if (pointers[indexOfMin] >= allDocArrays[indexOfMin].length) {
    lastVisibleDocs[indexOfMin] = minDoc;
    allDocArrays[indexOfMin] = await getNextDocs(indexOfMin, false);
  }
  return minDoc.data();
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
