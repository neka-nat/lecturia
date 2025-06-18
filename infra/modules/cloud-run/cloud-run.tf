variable "gcp_project_id" {}
variable "name" {}
variable "primary_region" {}
variable "repository_url" {}
variable "service_account_email" {}
variable "command" { type = string }
variable "args" { type = list(string) }
variable "env"        { type = map(string) }
variable "secret_env" { type = map(string) }
variable "public_access" { type = bool }
variable "required_apis" {}

resource "google_cloud_run_v2_service" "service" {
  name     = var.name
  location = var.primary_region
  ingress  = "INGRESS_TRAFFIC_ALL"
  template {
    service_account = var.service_account_email
    containers {
      image = "${var.repository_url}:latest"

      command = [var.command]
      args    = var.args

      dynamic "env" {
        for_each = var.env
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.secret_env
        content {
          name      = env.key
          value_source {
            secret_key_ref {
              secret  = split("/versions/", env.value)[0]
              version = split("/versions/", env.value)[1]
            }
          }
        }
      }
      resources {
        limits = {
          memory = "2Gi"
          cpu    = "1000m"
        }
      }
    }
  }

  traffic {
    percent         = 100
    type            = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [var.required_apis]
}

resource "google_cloud_run_service_iam_member" "public" {
  count    = var.public_access ? 1 : 0
  project  = var.gcp_project_id
  location = var.primary_region
  service  = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "url" { value = google_cloud_run_v2_service.service.uri }
