import os

from google.cloud import storage
from loguru import logger


_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME = os.environ["GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME"]


def get_storage_url(bucket_name: str, path: str) -> str:
    if "STORAGE_EMULATOR_HOST" in os.environ:
        return f"http://{os.environ['STORAGE_EMULATOR_HOST']}/storage/v1/b/{bucket_name}/o/{path}?alt=media"
    else:
        return f"https://storage.googleapis.com/{bucket_name}/{path}"


def get_public_storage_url(path: str) -> str:
    return get_storage_url(_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME, path)


def upload_data(
    data: bytes | str,
    path: str,
    bucket_name: str,
    mime_type: str = "application/octet-stream",
) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(path)
    blob.upload_from_string(data, content_type=mime_type)
    return get_storage_url(bucket_name, path)


def upload_data_to_public_bucket(
    data: bytes | str,
    path: str,
    mime_type: str = "application/octet-stream",
) -> str:
    return upload_data(data, path, _GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME, mime_type)


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


def count_public_bucket(prefix: str = "") -> int:
    client = storage.Client()
    blobs = client.list_blobs(_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME, prefix=prefix)
    return sum(1 for _ in blobs)


def download_data_from_public_bucket(path: str) -> bytes | None:
    try:
        client = storage.Client()
        bucket = client.bucket(_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME)
        blob = bucket.blob(path)
        return blob.download_as_bytes()
    except Exception as e:
        logger.error(f"Error downloading data from public bucket: {e}")
        return None


def delete_data_from_public_bucket(path: str):
    client = storage.Client()
    bucket = client.bucket(_GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME)

    if not path.endswith("/"):
        path += "/"

    blobs_iter = client.list_blobs(bucket, prefix=path)

    batch = []
    for blob in blobs_iter:
        batch.append(blob)
        if len(batch) == 100:
            bucket.delete_blobs(batch)
            batch.clear()

    if batch:
        bucket.delete_blobs(batch)
