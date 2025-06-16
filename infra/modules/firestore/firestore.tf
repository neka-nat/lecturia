variable "gcp_project_id" {}
variable "required_apis"  {}

# Firestore (native モード)
resource "google_firestore_database" "default" {
  project  = var.gcp_project_id
  name     = "(default)"
  location_id = "asia-northeast1"
  type     = "FIRESTORE_NATIVE"
  depends_on = [var.required_apis]
}

output "database_name" { value = google_firestore_database.default.name }
