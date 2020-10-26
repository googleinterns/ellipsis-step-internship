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

#TODO: add function that extracts color_depth and compression_ratio

class ImageAttributes():
    """ This class presents the attrebutes we nead to extracy from each image."""
     
    def __init__(self, url, provider_type, date_upload, date_taken, location, format, attribution, compression_ratio, color_depth, resolution): 
        self.url = url
        self.provider_type = provider_type
        self.date_upload = date_upload
        self.date_taken = date_taken
        self.location = location
        self.attribution = attribution
        self.compression_ratio=compression_ratio
        self.format = format
        self.color_depth=color_depth
        self.resolution= resolution

    def __str__(self):
        return str(self.url)+ "\n" + \
         str(self.location)+ "\n" +  \
         str(self.attribution)+ "\n" + \
         str(self.date_upload)+ "\n" 
         

    
    

