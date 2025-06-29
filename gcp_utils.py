# gcp_utils.py
import os
from google.cloud import storage
import vertexai
from vertexai.preview.generative_models import Part # Used for image generation Part type
import mimetypes

from config import GCP_PROJECT_ID, GCP_LOCATION, GCS_BUCKET_NAME

storage_client = storage.Client(project=GCP_PROJECT_ID)


def initialize_gcp_clients():
    """Initializes Vertex AI and Google Cloud Storage clients."""
    global storage_client # <--- ADD THIS LINE
    try:
        vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        print(f"Connected to GCP Project: `{GCP_PROJECT_ID}` in `{GCP_LOCATION}`")
        print(f" Using GCS Bucket: `{GCS_BUCKET_NAME}` for temporary files.")
        return True
    except Exception as e:
        print(f"Failed to initialize GCP clients: {e}")
        return False

def upload_to_gcs(file_path: str, destination_blob_name: str) -> str:
    """Uploads a file to the GCS bucket."""
    if not storage_client:
        raise Exception("GCS client not initialized. Call initialize_gcp_clients() first.")
    
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    gcs_uri = f"gs://{GCS_BUCKET_NAME}/{destination_blob_name}"
    print(f" Uploaded `{os.path.basename(file_path)}` to `{gcs_uri}`")
    return gcs_uri

def download_from_gcs(gcs_uri: str) -> bytes:
    if gcs_uri.startswith("gs://"):
        if not storage_client:
            raise Exception("GCS client not initialized. Call initialize_gcp_clients() first.")
            
        blob = storage.Blob.from_string(gcs_uri, client=storage_client)
        print(f"Downloading `{gcs_uri}` from GCS...")
        return blob.download_as_bytes()
    else:
        try:
            print(f"Reading local file `{gcs_uri}`...")
            with open(gcs_uri, "rb") as f: # If not GCS URI reading the local file
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read local file `{gcs_uri}`: {e}")


def get_mime_type(file_path: str) -> str:
    """Guesses the MIME type of a file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else "application/octet-stream" # Default to a generic binary type
