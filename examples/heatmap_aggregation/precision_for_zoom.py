#python3
"""
  Copyright 2020 Google LLC
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
 
    https://www.apache.org/licenses/LICENSE-2.0
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
 """

import geopy.distance
import geohash2
import numpy as np
import math

latlong_sf = (37.7749, 122.4194)

def get_quantization_error(precision=12):
  """Computes the quantization error for a certain geohash precision (for San Francisco)."""
  location_and_error_margin = np.array(geohash2.decode_exactly(geohash2.encode(latlong_sf[0],latlong_sf[1], precision=precision)))
  location = location_and_error_margin[0:2]
  error_margin = location_and_error_margin[2:]
  error_in_meters = geopy.distance.distance(location-error_margin, location+error_margin).m
  return error_in_meters



def zoom_to_meters_per_pixel(zoom):
  """Computes the meters in each pixel on Google maps  (for San Francisco).

  This corresponds to the fomula provided by
  https://groups.google.com/g/google-maps-js-api-v3/c/hDRO4oHVSeM/m/osOYQYXg2oUJ

  Args:
    zoom: Google Maps Zoom level

  Returns:
    meters_per_pixel: the size of a pixel in meters.

  """
  return 156543.03392 * math.cos(latlong_sf[0] * math.pi / 180) / math.pow(2, zoom)

digits2error = {num_digits: get_quantization_error(num_digits) for num_digits in range(0,23)}
if __name__ == "__main__":
  for zoom in range(0, 20):
    meters_per_pixel = zoom_to_meters_per_pixel(zoom)
    num_digits = [d for (d, error_in_meters) in digits2error.items() if error_in_meters < meters_per_pixel][0]
    print(f'zoom {zoom} needs {num_digits} geohash digits (meters_per_pixel: {meters_per_pixel}, error: {digits2error[num_digits]})')


