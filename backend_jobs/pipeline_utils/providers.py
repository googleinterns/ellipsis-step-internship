from backend_jobs.ingestion_pipeline.providers import image_provider_flickr
#This map provides all the Providers.ImageProviders in the platform
IMAGE_PROVIDERS = {'FlickrProvider': image_provider_flickr.FlickrProvider}