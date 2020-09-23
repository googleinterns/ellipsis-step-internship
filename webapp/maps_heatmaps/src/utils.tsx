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

import * as firebase from "firebase";
import { validateCoordinates } from "geokit";

/* This function converts from a google.maps.LatLng to a firebase.firestore.GeoPoint.*/
export function convertLatLngToGeopoint(
  position: google.maps.LatLng | null | undefined
): firebase.firestore.GeoPoint | undefined {
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
export function convertGeopointToLatLon(
  center: firebase.firestore.GeoPoint
): google.maps.LatLng {
  const geoPoint = center;
  const lat = geoPoint.latitude;
  const lng = geoPoint.longitude;
  const latlon = new google.maps.LatLng(lat, lng);
  return latlon;
}

export function getRadius(
  bounds: google.maps.LatLngBounds | null | undefined
): number {
  let newRadius = 2;
  if (bounds) {
    const meterRadius = google.maps.geometry.spherical.computeDistanceBetween(
      bounds.getCenter(),
      bounds.getNorthEast()
    );
    newRadius = meterRadius * 0.000621371192; //convert to miles
  }
  return newRadius;
}

export function toLatLngLiteral(
  coords: google.maps.LatLng
): { lat: number; lng: number } {
  return { lat: coords.lat(), lng: coords.lng() };
}

/*Checks if the document's coordinates is inside the visible current map.*/
//TODO: check waht to do if bounds are null.
export function isInVisibleMap(
  docData: firebase.firestore.DocumentData,
  map: google.maps.Map
): boolean {
  const bounds = map.getBounds();
  if (bounds != null) {
    const lat = docData.coordinates.lat();
    const lng = docData.coordinates.lng();
    const northEast = bounds.getNorthEast();
    const southWest = bounds.getSouthWest();
    const maxLat = northEast.lat();
    const maxLng = northEast.lng();
    const minLat = southWest.lat();
    const minLng = southWest.lng();
    return lat < maxLat && lat > minLat && lng < maxLng && lng > minLng;
  }
  return true;
}

export async function updateNumOfResults(
  queriedCollection: firebase.firestore.Query
): Promise<void> {
  const numOfResults = (await queriedCollection.get()).docs.length;
  const elementById = document.getElementById("num-of-results");
  if (elementById != null) {
    elementById.innerHTML = numOfResults + " images found";
  }
}
