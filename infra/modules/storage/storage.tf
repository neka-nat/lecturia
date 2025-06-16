variable "gcp_project_id" {}
variable "bucket_name" {}
variable "public_read"  { type = bool }
variable "required_apis" {}

resource "google_storage_bucket" "public" {
  name          = var.bucket_name
  project       = var.gcp_project_id
  location      = "US"          # マルチリージョンで可。必要に応じて変更
  uniform_bucket_level_access = true
  force_destroy = true          # ステージ環境なら true が楽
  depends_on    = [var.required_apis]
}

# オブジェクト公開
resource "google_storage_bucket_iam_member" "all_users_reader" {
  bucket = google_storage_bucket.public.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
  condition {
    title       = "PublicAccess"
    description = "Allow public read"
    expression  = var.public_read ? "true" : "false"
  }
}

output "bucket_name" { value = google_storage_bucket.public.name }
