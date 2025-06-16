variable "name" {}
variable "location" {}
variable "image" {}
variable "service_account_email" {}
variable "env"        { type = map(string) }
variable "secret_env" { type = map(string) }    # name => secret version resource id
variable "public_access" { type = bool }
variable "required_apis" {}

resource "google_cloud_run_v2_service" "service" {
  name     = var.name
  location = var.location
  ingress  = "INGRESS_TRAFFIC_ALL"
  template {
    service_account = var.service_account_email
    containers {
      image = var.image

      dynamic "env" {
        for_each = var.env
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "secret_env" {
        for_each = var.secret_env
        content {
          name      = secret_env.key
          value_source {
            secret_key_ref {
              secret  = secret_env.key
              version = secret_env.value
            }
          }
        }
      }
      resources {
        limits = {
          memory = "1Gi"
          cpu    = "1"
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

# Public ルーティング（必要なら off に）
resource "google_cloud_run_service_iam_member" "public" {
  count    = var.public_access ? 1 : 0
  location = var.location
  project  = var.service_account_email |> split("@")[1] |> join("")
  service  = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "url" { value = google_cloud_run_v2_service.service.uri }
