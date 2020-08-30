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
// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
function getPointsFromDB(
  heatmap: google.maps.visualization.HeatmapLayer,
  dataRef: geofirestore.GeoQuery
) {
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

function getGeoPointsFromDB() {
  const GeoFirestore = geofirestore.initializeApp(database);
  const geocollection = GeoFirestore.collection("images");
  geocollection
    .where("year", "==", 1999)
    .get()
    .then((value) => console.log(value.docs));
  geocollection.get().then((value) => console.log(value.docs));
  // Query using GeoPoint
  const center = new firebase.firestore.GeoPoint(37.77687, -122.438239);
  geocollection
    .near({
      center: center,
      radius: 1000000000,
    })
    .get()
    .then((value) => console.log(value.docs));
  getGeoPointsNearBy(37.77687, -122.438239, 1000);
}

/**Query by distance- has a problem */
function getGeoPointsNearBy(
  latitude: number,
  longitude: number,
  distance: number
) {
  // ~1 mile of lat and lon in degrees
  const lat = 0.0144927536231884;
  const lon = 0.0181818181818182;
  const lowerLat = latitude - lat * distance;
  const lowerLon = longitude - lon * distance;

  const greaterLat = latitude + lat * distance;
  const greaterLon = longitude + lon * distance;

  const lesserGeopoint = new firebase.firestore.GeoPoint(lowerLat, lowerLon);
  const greaterGeopoint = new firebase.firestore.GeoPoint(
    greaterLat,
    greaterLon
  );

  database
    .collection("images")
    .where("location", ">=", lesserGeopoint)
    .where("location", "<=", greaterGeopoint)
    .get()
    .then((value) => console.log(value.docs));
  //return dataRef;
}

export { getPointsFromDB, getGeoPointsFromDB, getQuiredCollection };
