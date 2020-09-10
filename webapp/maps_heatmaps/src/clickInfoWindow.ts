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

import { map } from "./index";
import { getQueriedCollection } from "./queryDB";
import * as firebase from "firebase";
import { GeoFirestoreTypes } from "geofirestore";

//TODO: run mocha tests on the browser.
let markers: Array<google.maps.Marker> = [];

/* querys for 20 random docs in the database in order to place markers on them. */
//TODO: make this function more random.
//TODO: use this function to show images on the side pannel-so they will correlate (relocate to a different file)
async function setFirstTwentyMarkers(
  center: firebase.firestore.GeoPoint,
  radius: number,
  labels: string[],
  year?: number,
  month?: number
): Promise<void> {
  let lastInfoWindow: google.maps.InfoWindow | null = new google.maps.InfoWindow();
  const dataref = await (
    await getQueriedCollection(center, radius, labels, year, month).get()
  ).docs;
  eraseAllMarkers();
  const jump = Math.ceil(dataref.length / 10);
  for (let i = 0; i < dataref.length; i = i + jump) {
    addMarkerWithListener(
      map,
      convertGeopointTolatlon(dataref[i].data().g.geopoint),
      dataref[i].data().labels,
      year,
      month
    );
  }

  //TODO: after runing mocha tests on the browser, remove this function out of setFirstTwentyMarkers.
  /* placing a marker with a click event in a given location. 
   when clicking on the marker an infoWindow will appear 
   with all the information on this location from the database. */
  function addMarkerWithListener(
    map: google.maps.Map,
    latlng: google.maps.LatLng,
    labels: string[],
    year?: number,
    month?: number
  ) {
    const InfoWindow: google.maps.InfoWindow = new google.maps.InfoWindow();
    const marker = new google.maps.Marker({
      position: latlng,
      map: map,
    });
    markers.push(marker);
    google.maps.event.addListener(marker, "click", async () => {
      const center = convertLatlngToGeopoint(marker.getPosition());
      if (center !== undefined) {
        const dataref = await (
          await getQueriedCollection(center, 0, labels, year, month).get()
        ).docs[0];
        InfoWindow.setContent(
          getInfoWindowContent(
            getLabels(dataref.data()),
            getUrl(dataref.data()),
            getDate(dataref.data()),
            getAttribution(dataref.data())
          )
        );
        if (lastInfoWindow !== null) lastInfoWindow.close();
        InfoWindow.open(map, marker);
        lastInfoWindow = InfoWindow;
      }
    });
  }
}

/* this function renders information for the info window, in html format.
   @param mylabels - all the labels this image has, 
   @param myurl - the image url,
   @param mydate - the date the image was taken,
   @param myattribution - who uplouded the image, */
function getInfoWindowContent(
  mylabels: string,
  myurl: string,
  mydate: string,
  myattribution: string
): string {
  const contentString =
    "<div class='map-info-window'>" +
    "<img class='fit-image' src=" +
    myurl +
    "></div>" +
    "<div style='float:right; padding: 10px;'>" +
    "<p class='fit-text'>" +
    mylabels +
    mydate +
    myattribution +
    "</p></div>";
  return contentString;
}

function getLabels(dataref: GeoFirestoreTypes.GeoDocumentData) {
  let content = "<b>Labels: </b>";
  dataref.labels.forEach((element: string) => {
    content += element;
    content += " ";
  });
  content += "<br/>";
  return content;
}

function getDate(dataref: GeoFirestoreTypes.GeoDocumentData) {
  const content =
    "<b>Date: </b>" +
    dataref.day +
    "/" +
    dataref.month +
    "/" +
    dataref.year +
    "<br/>";
  return content;
}

function getUrl(dataref: GeoFirestoreTypes.GeoDocumentData) {
  const content = dataref.url;
  return content;
}

//TODO: add field attribute to database and extract attribute field in this function.
function getAttribution(dataref: GeoFirestoreTypes.GeoDocumentData) {
  const content = "<b>Attribution: </b>uploader of the image_______ <br/>";
  return content;
}

function convertLatlngToGeopoint(
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

function convertGeopointTolatlon(center: firebase.firestore.GeoPoint) {
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
