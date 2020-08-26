import { database } from "./index";
import * as firebase from "firebase";
import * as geofirestore from "geofirestore";

/* returns the filtered collection by the different queries*/
function getQuiredCollection(
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

/* displays the relevant images on the map
given the filtered collection and the heapmap*/
function getPointsFromDB(
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
  });
}

function getLatLon(coordinates: firebase.firestore.GeoPoint) {
  const lat = coordinates.latitude;
  const lng = coordinates.longitude;
  return new google.maps.LatLng(lat, lng);
}

export { getPointsFromDB, getQuiredCollection };
