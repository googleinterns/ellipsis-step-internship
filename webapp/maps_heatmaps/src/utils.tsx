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
import { LatLng } from "./interface";

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

/* This function converts from a google.maps.LatLng to a LatLngLiteral.*/
export function toLatLngLiteral(coords: google.maps.LatLng): LatLng {
  return { lat: coords.lat(), lng: coords.lng() };
}

/*Checks if the document's coordinates are inside the visible current map.*/
//TODO: check what to do if bounds are null.
export function isInVisibleMap(
  docData: firebase.firestore.DocumentData,
  map: google.maps.Map
): boolean {
  const bounds = map.getBounds();
  if (bounds != null) {
    const lat = docData.coordinates.latitude;
    const lng = docData.coordinates.longitude;
    const northEast = bounds.getNorthEast();
    const southWest = bounds.getSouthWest();
    const maxLat = northEast.lat();
    const maxLng = northEast.lng();
    const minLat = southWest.lat();
    const minLng = southWest.lng();
    if (minLat < maxLat && minLng < maxLng) {
      //Current visible map's borders are valid.
      return lat < maxLat && lat > minLat && lng < maxLng && lng > minLng;
    }
    if (minLng < maxLng) {
      //Current visible map's top borders are more south then it's buttom borders.
      //Longtitude is valid.
      return (
        lng < maxLng &&
        lng > minLng &&
        isInVisibleMapInvalidLatitude(minLat, maxLat, lat)
      );
    }
    if (minLat < maxLat) {
      //Current visible map's right borders are more west then it's left borders.
      //Latitude is valid.
      return (
        lat < maxLat &&
        lat > minLat &&
        isInVisibleMapInvalidLongtitude(minLng, maxLng, lng)
      );
    }
    // Current visible map's borders are invalid in both longtitude and latitude.
    return (
      isInVisibleMapInvalidLatitude(minLat, maxLat, lat) &&
      isInVisibleMapInvalidLongtitude(minLng, maxLng, lng)
    );
  }
  return true;
}

/*Checks if the point is in the visible map when the map's latitude borders are invalid. */
function isInVisibleMapInvalidLatitude(
  minLat: number,
  maxLat: number,
  pointLat: number
): boolean {
  return (
    (pointLat < 90 && pointLat > minLat) ||
    (pointLat < maxLat && pointLat > -90)
  );
}

/*Checks if the point is in the visible map when the map's longtitude borders are invalid. */
function isInVisibleMapInvalidLongtitude(
  minLng: number,
  maxLng: number,
  pointLng: number
): boolean {
  return (
    (pointLng < 180 && pointLng > minLng) ||
    (pointLng < maxLng && pointLng > -180)
  );
}

/*@return Coordinates of the point that is in the middle of the two given coordinates. */
export function findMidCoordinates(pointA: LatLng, pointB: LatLng): LatLng {
  const midLat = (pointA.lat + pointB.lat) / 2;
  const midLng = (pointA.lng + pointB.lng) / 2;
  return { lat: midLat, lng: midLng };
}
