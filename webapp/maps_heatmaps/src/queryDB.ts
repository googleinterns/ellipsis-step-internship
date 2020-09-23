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

/*
function getAllQueriedCollections(
  hashs: string[],
  labels: string[],
  datetime: DateTime
): firebase.firestore.Query {
  let allQueriedCollection: firebase.firestore.Query;
  hashs.forEach((hash: string) => {
    const queriedCollection = getQueriedCollection(hash, labels, datetime);
    allQueriedCollection = allQueriedCollection + queriedCollection;
  });
}*/

/* @param center The center of the current map, 
   @param radius The radius of the circle that contains the current map bounderies
   @param labels The labels the client queries by
   @param year, month, day The date the client queries by
   @return The filtered collection by the different queries*/
function getQueriedCollection(
  hash: string,
  labels: string[],
  datetime: DateTime
): firebase.firestore.Query {
  const hashfield: string = "hashmap.hash" + hash.length;
  let dataRef = databaseCollection
    .where(hashfield, "==", hash)
    .where("labels", "array-contains-any", labels);
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
  return dataRef.orderBy("random");
}

/* Displays the relevant images on the map
given the filtered collection and the heapmap. */
function updateHeatmapFromQuery(
  heatmap: google.maps.visualization.HeatmapLayer,
  dataRef: firebase.firestore.Query
): void {
  const allPoints: Array<google.maps.LatLng> = [];
  dataRef.get().then((querySnapshot) => {
    querySnapshot.forEach((doc) => {
      const coordinates = doc.data().coordinates;
      const newLatLon = getLatLon(coordinates);
      allPoints.push(newLatLon);
    });
    heatmap.setData(allPoints);
  });
}

function getLatLon(coordinates: firebase.firestore.GeoPoint) {
  const lat = coordinates.latitude;
  const lng = coordinates.longitude;
  return new google.maps.LatLng(lat, lng);
}

export { updateHeatmapFromQuery, getQueriedCollection };
