variable "gcp_project_id" {}
variable "required_apis" {}

resource "google_service_account" "app" {
  account_id   = "lecturia-app-sa"
  display_name = "Lecturia App Service Account"
  project      = var.gcp_project_id
  depends_on   = [var.required_apis]
}

resource "google_service_account" "worker" {
  account_id   = "lecturia-worker-sa"
  display_name = "Lecturia Worker Service Account"
  project      = var.gcp_project_id
  depends_on   = [var.required_apis]
}

# 必要最低限の IAM 権限
locals {
  roles_app = [
    "roles/datastore.user",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectViewer",
    "roles/cloudtasks.enqueuer",
    "roles/artifactregistry.reader",
  ]
  roles_worker = [
    "roles/datastore.user",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin",
    "roles/artifactregistry.reader",
    "roles/aiplatform.user",
  ]
}

resource "google_project_iam_member" "app_roles" {
  for_each = toset(local.roles_app)
  project  = var.gcp_project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.app.email}"
}

resource "google_project_iam_member" "worker_roles" {
  for_each = toset(local.roles_worker)
  project  = var.gcp_project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.worker.email}"
}

output "app_sa_email"    { value = google_service_account.app.email }
output "worker_sa_email" { value = google_service_account.worker.email }
