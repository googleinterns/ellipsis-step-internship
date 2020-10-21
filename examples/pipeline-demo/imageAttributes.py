


class ImageAttributes():
    url=0
    provider_type=0
    date_upload=0
    date_taken=0
    location=0
    format=0
    def __init__(self, url, provider_type, date_upload, date_taken, location, format, attribution, compression_ratio, color_depth):
        self.url = url
        self.provider_type = provider_type
        self.date_upload = date_upload
        self.date_taken = date_taken
        self.location = location
        self.attribution = attribution
        self.compression_ratio=compression_ratio
        self.format = format
        self.color_depth=color_depth

    def __str__(self):
         return str(self.url)+"   " +str(self.location)

    
    

