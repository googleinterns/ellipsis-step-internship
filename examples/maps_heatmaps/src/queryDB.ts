import { database } from "./index";
import * as firebase from "firebase";
import * as geofirestore from "geofirestore";

/* returns the filtered collection by the different queries*/
function getQuiredCollection(
  labels: string[],
  year?: number,
  month?: number,
  day?: number
): firebase.firestore.Query {
  let dataRef: firebase.firestore.Query = database
    .collection("images")
    .where("labels", "array-contains-any", labels);
  if (year != undefined) dataRef = dataRef.where("year", "==", year);
  if (year != undefined && month != undefined)
    dataRef = dataRef.where("month", "==", month);
  if (year != undefined && month != undefined && day != undefined)
    dataRef = dataRef.where("day", "==", day);
  return dataRef;
}

/* displays the relevant images on the map
given the filtered collection and the heapmap*/
// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
function getPointsFromDB(
  heatmap: google.maps.visualization.HeatmapLayer,
  dataRef: firebase.firestore.Query
) {
  const allPoints: Array<google.maps.LatLng> = [];
  dataRef.get().then((querySnapshot) => {
    querySnapshot.forEach((doc) => {
      const coordinates: firebase.firestore.GeoPoint = doc.get("coordinates");
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

export { getPointsFromDB, getQuiredCollection };
