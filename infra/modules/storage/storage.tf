variable "gcp_project_id" {}
variable "bucket_name" {}
variable "primary_region" {}
variable "public_read" {          # 読み取り公開／非公開フラグ
  type    = bool
  default = true
}
variable "writer_sa_email" {
  type = string
}
variable "required_apis" {}

resource "google_storage_bucket" "public" {
  name          = var.bucket_name
  project       = var.gcp_project_id
  location      = var.primary_region
  uniform_bucket_level_access = true
  force_destroy = true          # ステージ環境なら true
  depends_on    = [var.required_apis]
}

resource "google_storage_bucket_iam_member" "all_users_reader" {
  count  = var.public_read ? 1 : 0   # true なら 1 件作成、false なら 0 件
  bucket = google_storage_bucket.public.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_storage_bucket_iam_member" "writer_sa" {
  bucket = google_storage_bucket.public.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.writer_sa_email}"
}

output "bucket_name" {
  value = google_storage_bucket.public.name
}
