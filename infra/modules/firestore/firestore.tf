variable "gcp_project_id" {}
variable "primary_region" {}
variable "required_apis"  {}

# Firestore (native モード)
resource "google_firestore_database" "default" {
  project  = var.gcp_project_id
  name     = "(default)"
  location_id = var.primary_region
  type     = "FIRESTORE_NATIVE"
  depends_on = [var.required_apis]
}

output "database_name" { value = google_firestore_database.default.name }
