variable "gcp_project_id" {}
variable "primary_region" {
  type = string
}
variable "repository_id" {
  type = string
}
variable "required_apis" {
  description = "必要なAPI"
}


locals {
  repo_id   = var.repository_id
  image_tag = "latest"
  image_uri = "${var.primary_region}-docker.pkg.dev/${var.gcp_project_id}/${local.repo_id}/${var.repository_id}:${local.image_tag}"
}

resource "google_artifact_registry_repository" "lecturia_container_registry" {
  project       = var.gcp_project_id
  location      = var.primary_region
  repository_id = var.repository_id
  description   = "Lecturia Container Registry"
  format        = "DOCKER"
  depends_on = [
    var.required_apis
  ]
}

resource "null_resource" "submit" {
  provisioner "local-exec" {
    command = "gcloud builds submit --tag ${local.image_uri} ${path.module}/../../../api"
  }
}

output "repository_url" {
  value = local.image_uri
}
