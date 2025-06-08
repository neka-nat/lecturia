from google.cloud import storage
from loguru import logger


_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME = "lecturia-public-storage"
_GOOGLE_CLOUD_STORAGE_PRIVATE_BUCKET_NAME = "lecturia-private-storage"


def upload_data(data: bytes | str, path: str, bucket_name: str) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    return f"https://storage.googleapis.com/{bucket_name}/{path}"


def upload_data_to_public_bucket(data: bytes | str, path: str) -> str:
    return upload_data(data, path, _GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME)


def upload_data_to_private_bucket(data: bytes | str, path: str) -> str:
    return upload_data(data, path, _GOOGLE_CLOUD_STORAGE_PRIVATE_BUCKET_NAME)


def is_exists_in_public_bucket(path: str) -> bool:
    client = storage.Client()
    bucket = client.bucket(_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME)
    blob = bucket.blob(path)
    return blob.exists()


def ls_public_bucket(prefix: str = "") -> list[str]:
    client = storage.Client()
    blobs = client.list_blobs(_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME, prefix=prefix)
    directories = set()
    for blob in blobs:
        dirs = blob.name.split("/")
        if dirs[0] == prefix and len(dirs[1:]) > 1:
            directories.add(dirs[1])
    return list(directories)


def download_data_from_public_bucket(path: str) -> bytes | None:
    try:
        client = storage.Client()
        bucket = client.bucket(_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME)
        blob = bucket.blob(path)
        return blob.download_as_bytes()
    except Exception as e:
        logger.error(f"Error downloading data from public bucket: {e}")
        return None
