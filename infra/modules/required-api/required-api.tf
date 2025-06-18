resource "google_project_service" "required_apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "firestore.googleapis.com",
    "cloudtasks.googleapis.com",
    "iamcredentials.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false
}

output "required_apis" {
  value = google_project_service.required_apis
}
