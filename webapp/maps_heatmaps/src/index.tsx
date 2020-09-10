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

// [START maps_layer_heatmap]
// This example requires the Visualization library. Include the libraries=visualization
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">

// Imports
let map: google.maps.Map, heatmap: google.maps.visualization.HeatmapLayer;
import * as firebase from "firebase";
import firebaseConfig from "./firebase_config";
import * as geofirestore from "geofirestore";
import { database } from "./declareDatabase";
import * as queryDB from "./queryDB";
import { setFirstTwentyMarkers } from "./clickInfoWindow";

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
  map.addListener("center_changed", async () => await mapChanged());
  map.addListener("zoom_changed", async () => await mapChanged());
  //TODO: labels, year and month should be as the client requested, not fixed values.
  async function mapChanged() {
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
    const queriedCollection = queryDB.getQueriedCollection(
      newCenter,
      newRadius,
      ["dog", "bag"]
    );
    queryDB.updateHeatmapFromQuery(heatmap, queriedCollection);
    //TODO: setfirsttwentymarkers by field that where submitted.
    await setFirstTwentyMarkers(
      newCenter,
      newRadius,
      ["cat", "dog", "bag"],
      1999
    );
  }
}

// [END maps_layer_heatmap]

export { initMap, database, map };
