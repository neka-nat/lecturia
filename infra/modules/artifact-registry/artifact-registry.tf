variable "gcp_project_id" {}
variable "artifact_registry_location" {
  type = string
  description = "Artifact Registry のロケーションをどこにするか"
}
variable "required_apis" {
  description = "必要なAPI"
}

resource "google_artifact_registry_repository" "lecturia_api" {
  project       = var.gcp_project_id
  location      = var.artifact_registry_location
  repository_id = "lecturia-api"
  description   = "Lecturia API server"
  format        = "DOCKER"
  depends_on = [
    var.required_apis
  ]
}
