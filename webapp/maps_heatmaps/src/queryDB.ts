/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
/* eslint-disable @typescript-eslint/no-unused-vars */
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

import { database } from "./index";
import * as firebase from "firebase";
import { DateTime } from "./interface";

const databaseCollection = database.collection("Images");

/* This function gets a document by its id*/
async function getDocById(id: string) {
  return (await database.collection("Images").doc(id).get()).data();
}

/* Queries for docs in firebase by given data such as labels, date and hash. 
   the function returns a reference to the queried data.
   @param labels The labels the client queries by
   @param datetime The date the client queries by
   @param hash The hash of the current map bounderies
   @return The filtered collection by the different queries*/
function getQueriedCollection(
  labels: string[],
  datetime: DateTime,
  hash?: string
): firebase.firestore.Query {
  let dataRef = databaseCollection.where(
    "labels",
    "array-contains-any",
    labels
  );
  if (hash != undefined) {
    const hashfield: string = "hashmap.hash" + hash.length;
    dataRef = dataRef.where(hashfield, "==", hash);
  }
  if (datetime.year != undefined)
    dataRef = dataRef.where("date.year", "==", datetime.year);
  if (datetime.year != undefined && datetime.month != undefined)
    dataRef = dataRef.where("date.month", "==", datetime.month);
  if (
    datetime.year != undefined &&
    datetime.month != undefined &&
    datetime.day != undefined
  )
    dataRef = dataRef.where("date.day", "==", datetime.day);
  return dataRef;
}

/* Displays the relevant images on the map
given the filtered collection and the heapmap. */
async function updateHeatmapFromQuery(
  heatmap: google.maps.visualization.HeatmapLayer,
  dataRefs: firebase.firestore.Query[]
): Promise<void> {
  const allPoints: Array<google.maps.LatLng> = [];
  for (const dataRef of dataRefs) {
    const docs = (await dataRef.get()).docs;
    for (const doc of docs) {
      const coordinates = doc.data().coordinates;
      const newLatLon = getLatLon(coordinates);
      allPoints.push(newLatLon);
    }
  }
  heatmap.setData(allPoints);
}

function getLatLon(coordinates: firebase.firestore.GeoPoint) {
  const lat = coordinates.latitude;
  const lng = coordinates.longitude;
  return new google.maps.LatLng(lat, lng);
}

export { updateHeatmapFromQuery, getQueriedCollection, getDocById };
