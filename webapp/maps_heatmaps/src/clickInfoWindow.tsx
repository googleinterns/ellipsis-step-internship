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
import { DateTime } from "./interface";
import { convertLatLngToGeopoint } from "./utils";

import React from "react";
import ReactDOMServer from "react-dom/server";
import InfoWindowContent from "./components/infoWindowContent";

//TODO: run mocha tests on the browser.
let markers: Array<google.maps.Marker> = [];
let infoWindow: google.maps.InfoWindow | null = null;

/* Placing a marker with a click event in a given location. 
   When clicking on the marker an infoWindow will appear 
   with all the information on this location from the database. 
   @param image The image we add a click listener
   @param map The map we place markers
   @param latlng The coordinates of the image
   @param hash The hash of the current map bounderies
   @param labels The labels the client queries by
   @param datetime The date the client queries by */
function addMarkerWithListener(
  image: HTMLImageElement,
  map: google.maps.Map,
  latlng: google.maps.LatLng,
  hash: string,
  labels: string[],
  datetime: DateTime
): void {
  const marker = new google.maps.Marker({
    position: latlng,
    map: map,
  });
  if (infoWindow === null) {
    infoWindow = new google.maps.InfoWindow();
  }
  markers.push(marker);
  image.addEventListener("click", async () =>
    openInfoWindow(infoWindow, marker, hash, labels, datetime)
  );
  google.maps.event.addListener(marker, "click", async () =>
    openInfoWindow(infoWindow, marker, hash, labels, datetime)
  );
}

/* This function creates and opens a infoWindow on a specific marker
   @param infoWindow The infoWindow we will open with new information
   @param marker The marker we will open a infoWindow
   @param hash The hash of the image
   @param labels The labels the client queries by
   @param datetime The date the client queries by */
async function openInfoWindow(
  infoWindow: google.maps.InfoWindow | null,
  marker: google.maps.Marker,
  hash: string,
  labels: string[],
  dateTime: DateTime
) {
  const center = convertLatLngToGeopoint(marker.getPosition());
  if (center !== undefined) {
    const dataref = await (
      await getQueriedCollection(hash, labels, dateTime).get()
    ).docs[0];
    if (infoWindow !== null) {
      infoWindow.close();
      infoWindow.setContent(
        ReactDOMServer.renderToString(
          <InfoWindowContent
            labels={dataref.data().labels}
            url={dataref.data().url}
            dateTime={
              (dateTime = {
                year: dataref.data().date.year,
                month: dataref.data().date.month,
                day: dataref.data().date.day,
              })
            }
            attribution={dataref.data().attribution}
          />
        )
      );
      infoWindow.open(map, marker);
    }
  }
}

function eraseAllMarkers(): void {
  markers.forEach((marker) => {
    marker.setMap(null);
  });
  markers = [];
}

export { eraseAllMarkers, addMarkerWithListener };
