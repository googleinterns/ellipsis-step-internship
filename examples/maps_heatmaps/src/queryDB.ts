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
import * as geofirestore from "geofirestore";

/* @param center The center of the current map, 
   @param radius The radius of the circle that contains the current map bounderies
   @param labels The labels the client queries by
   @param year, month, day The date the client queries by
   @return The filtered collection by the different queries*/
function getQueriedCollection(
  center: firebase.firestore.GeoPoint,
  radius: number,
  labels: string[],
  year?: number,
  month?: number,
  day?: number
): geofirestore.GeoQuery {
  const GeoFirestore = geofirestore.initializeApp(database);
  const geoCollection = GeoFirestore.collection("images");
  let dataRef: geofirestore.GeoQuery = geoCollection
    .near({
      center: center,
      radius: radius,
    })
    .where("labels", "array-contains-any", labels);
  if (year != undefined) dataRef = dataRef.where("year", "==", year);
  if (year != undefined && month != undefined)
    dataRef = dataRef.where("month", "==", month);
  if (year != undefined && month != undefined && day != undefined)
    dataRef = dataRef.where("day", "==", day);
  return dataRef;
}

/* Displays the relevant images on the map
given the filtered collection and the heapmap. */
function updateHeatmapFromQuery(
  heatmap: google.maps.visualization.HeatmapLayer,
  dataRef: geofirestore.GeoQuery
): void {
  const allPoints: Array<google.maps.LatLng> = [];
  dataRef.get().then((querySnapshot) => {
    querySnapshot.forEach((doc) => {
      const coordinates: firebase.firestore.GeoPoint = doc.data().g.geopoint;
      const newLatLon = getLatLon(coordinates);
      allPoints.push(newLatLon);
    });
    heatmap.setData(allPoints);
    console.log(allPoints.length);
  });
}

function getLatLon(coordinates: firebase.firestore.GeoPoint) {
  const lat = coordinates.latitude;
  const lng = coordinates.longitude;
  return new google.maps.LatLng(lat, lng);
}

export { updateHeatmapFromQuery, getQueriedCollection };
