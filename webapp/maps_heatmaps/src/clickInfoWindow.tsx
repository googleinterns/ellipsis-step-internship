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
/* eslint-disable @typescript-eslint/no-unused-vars */

import { map } from "./index";
import { getQueriedCollection } from "./queryDB";
import * as firebase from "firebase";
import { DateTime } from "./interface";

import React from "react";
import ReactDOMServer from "react-dom/server";
import InfoWindowContent from "./components/infoWindowContent";

//TODO: run mocha tests on the browser.
let markers: Array<google.maps.Marker> = [];
let infoWindow: google.maps.InfoWindow | null = null;

/* Queries for 20 random dataPoints in the database in order to place markers on them. */
//TODO: make the function more random by having all makers equally separated on the map.
//We can do this by:
//1. Having a random field and ordering by it.
//2. Dividing the map into sections and in each section query for a datapoint.
//TODO: use this function to show images on the side panel-so they will correlate (relocate to a different file)
async function setFirstTwentyMarkers(
  center: firebase.firestore.GeoPoint,
  radius: number,
  labels: string[],
  datetime: DateTime
): Promise<void> {
  const dataref = await (
    await getQueriedCollection(center, radius, labels, datetime).get()
  ).docs;
  eraseAllMarkers();
  const jump = Math.ceil(dataref.length / 10);
  for (let i = 0; i < dataref.length; i = i + jump) {
    addMarkerWithListener(
      map,
      convertGeopointToLatLon(dataref[i].data().g.geopoint),
      dataref[i].data().labels,
      datetime
    );
  }
}

/* Placing a marker with a click event in a given location. 
   When clicking on the marker an infoWindow will appear 
   with all the information on this location from the database. */
function addMarkerWithListener(
  map: google.maps.Map,
  latlng: google.maps.LatLng,
  labels: string[],
  datetime: DateTime
) {
  const marker = new google.maps.Marker({
    position: latlng,
    map: map,
  });
  if (infoWindow === null) {
    infoWindow = new google.maps.InfoWindow();
  }
  markers.push(marker);
  google.maps.event.addListener(marker, "click", async () => {
    const center = convertLatLngToGeopoint(marker.getPosition());
    if (center !== undefined) {
      const dataref = await (
        await getQueriedCollection(center, 0, labels, datetime).get()
      ).docs[0];
      if (infoWindow !== null) {
        infoWindow.close();
        infoWindow.setContent(
          ReactDOMServer.renderToString(
            <InfoWindowContent
              labels={dataref.data().labels}
              url={dataref.data().url}
              dateTime={
                (datetime = {
                  year: dataref.data().year,
                  month: dataref.data().month,
                  day: dataref.data().day,
                })
              }
              //TODO: add attribution field to the database.
              attribution={""}
            />
          )
        );
        infoWindow.open(map, marker);
      }
    }
  });
}

/* This function converts from a google.maps.LatLng to a firebase.firestore.GeoPoint.*/
function convertLatLngToGeopoint(
  position: google.maps.LatLng | null | undefined
) {
  const latlng = position;
  if (latlng !== undefined && latlng !== null) {
    const lat = latlng.lat();
    const lng = latlng.lng();
    if (lat !== undefined && lng !== undefined) {
      const geoPoint = new firebase.firestore.GeoPoint(lat, lng);
      return geoPoint;
    }
  }
  return undefined;
}

/* This function converts from a firebase.firestore.GeoPoint to a google.maps.LatLng.*/
function convertGeopointToLatLon(center: firebase.firestore.GeoPoint) {
  const geoPoint = center;
  const lat = geoPoint.latitude;
  const lng = geoPoint.longitude;
  const latlon = new google.maps.LatLng(lat, lng);
  return latlon;
}

function eraseAllMarkers(): void {
  markers.forEach((marker) => {
    marker.setMap(null);
  });
  markers = [];
}

export { setFirstTwentyMarkers };
