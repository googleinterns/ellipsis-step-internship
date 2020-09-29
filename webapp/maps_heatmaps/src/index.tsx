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
import { database } from "./declareDatabase";
import * as queryDB from "./queryDB";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import React from "react";
import ReactDOM from "react-dom";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import SidePanel from "./components/sidepanel";
import { addImageToSidePanel, eraseAllImages } from "./sidepanelUtils";
import { eraseAllMarkers, addMarkerWithListener } from "./clickInfoWindow";
import {
  convertGeopointToLatLon,
  toLatLngLiteral,
  isInVisibleMap,
} from "./utils";
import { DateTime } from "./interface";
import { getGeohashBoxes } from "./geoquery";
import { MinOfLists } from "./MinOfLists";

let map: google.maps.Map, heatmap: google.maps.visualization.HeatmapLayer;
let selectedLabels: string[] = [];
let selectedDate: DateTime = {};
let timeOfLastRequest: number = Date.now();
let queriedCollections: firebase.firestore.Query[];
let lastVisibleDocs: firebase.firestore.QueryDocumentSnapshot<
  firebase.firestore.DocumentData
>[];
const NUM_OF_IMAGES_AND_MARKERS = 20;

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
  map.addListener("drag", () => mapChanged());
  map.addListener("zoom_changed", () => mapChanged());
  google.maps.event.addListenerOnce(map, "center_changed", () => mapChanged());
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
      toLatLngLiteral(bounds.getSouthWest())
    );
    //Check if it's the last request made.
    if (timeOfLastRequest === timeOfRequest) {
      queriedCollections = [];
      lastVisibleDocs = [];
      if (arrayhash.length === 0) {
        const queriedCollection = queryDB.getQueriedCollection(
          selectedLabels,
          selectedDate
        );
        //Check if it's the last request made.
        if (timeOfLastRequest === timeOfRequest) {
          queriedCollections.push(queriedCollection);
        }
      } else {
        arrayhash.forEach((hash: string) => {
          const queriedCollection = queryDB.getQueriedCollection(
            selectedLabels,
            selectedDate,
            hash
          );
          //Check if it's the last request made.
          if (timeOfLastRequest === timeOfRequest) {
            queriedCollections.push(queriedCollection);
          }
        });
      }
      await queryDB.updateHeatmapFromQuery(heatmap, queriedCollections);
      updateImagesAndMarkers(true);
    }
  }
}

/*@param index The index of the geohash box that we need the next docs from.
  @param first Determines whether this is a new collection and the next docs should be from the beginning,
  or should start after the last visible doc.*/
//TODO: Check if its is better to get less than 20 docs each time.
async function getNextDocs(index: number, first: boolean) {
  let docsArray: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[];
  if (!first && lastVisibleDocs[index]) {
    docsArray = (
      await queriedCollections[index]
        .orderBy("random")
        .startAfter(lastVisibleDocs[index])
        .limit(NUM_OF_IMAGES_AND_MARKERS)
        .get()
    ).docs;
  } else {
    docsArray = (
      await queriedCollections[index]
        .orderBy("random")
        .limit(NUM_OF_IMAGES_AND_MARKERS)
        .get()
    ).docs;
  }
  return docsArray;
}

/*@param first Determines whether this is a new collection and the next docs should be from the beginning,
  or should start after the last visible doc.
  Queries for random dataPoints in the database in order to place markers and images of it. */
//TODO: store all previous shown images and markers and add a 'previous' button.
async function updateImagesAndMarkers(first: boolean): Promise<void> {
  let countOfImagesAndMarkers = 0;
  const elementById = document.getElementById("images-holder");
  const allDocArrays: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[][] = new Array<
    firebase.firestore.QueryDocumentSnapshot<firebase.firestore.DocumentData>[]
  >(queriedCollections.length);
  //Array of the docs from each geohash box.
  const pointers: number[] = new Array<number>(queriedCollections.length);
  //Pointers to the last doc that was taken from each geohash box.
  for (let i = 0; i < queriedCollections.length; i++) {
    allDocArrays[i] = await getNextDocs(i, first);
    pointers[i] = 0;
  }
  const nextBtn = document.getElementsByTagName("button").namedItem("next-btn");
  if (nextBtn) nextBtn.disabled = false;
  eraseAllMarkers();
  eraseAllImages();
  if (elementById) {
    try {
      while (countOfImagesAndMarkers < NUM_OF_IMAGES_AND_MARKERS) {
        let minDocData;
        let minDoc;
        do {
          minDoc = await getMinDoc(allDocArrays, pointers);
          minDocData = minDoc.data();
        } while (!isInVisibleMap(minDocData, map));
        const latlng = convertGeopointToLatLon(minDocData.coordinates);
        const imageElement = addImageToSidePanel(minDocData, elementById);
        await addMarkerWithListener(
          imageElement,
          map,
          latlng,
          minDoc.id,
          minDocData.labels,
          selectedDate
        );
        countOfImagesAndMarkers++;
      }
    } catch (e) {
      //There are no more new docs to present.
      if (nextBtn) nextBtn.disabled = true;
      return;
    }
  }
}

//TODO: Figure out how not to give priority to the doc in the first geohash.
async function getMinDoc(
  allDocArrays: firebase.firestore.QueryDocumentSnapshot<
    firebase.firestore.DocumentData
  >[][],
  pointers: number[]
) {
  const getMinObject = new MinOfLists(
    (
      doc: firebase.firestore.QueryDocumentSnapshot<
        firebase.firestore.DocumentData
      >
    ) => doc.data().random
  );
  const minInfo = getMinObject.getMin(allDocArrays, pointers);
  const minDoc = minInfo.object;
  const indexOfMin = minInfo.index;
  pointers[indexOfMin]++;
  if (minDoc) {
    lastVisibleDocs[indexOfMin] = minDoc;
    if (pointers[indexOfMin] >= allDocArrays[indexOfMin].length) {
      // Done with all current docs of this geohash box, need to get next ones.
      pointers[indexOfMin] = 0;
      allDocArrays[indexOfMin] = await getNextDocs(indexOfMin, false);
    }
    return minDoc;
  }
  throw new Error("no more documents in queries");
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

export { initMap, database, queriesChanged, map, updateImagesAndMarkers };
