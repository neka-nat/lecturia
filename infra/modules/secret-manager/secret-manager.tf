variable "gcp_project_id" {}
variable "secrets_file" {}
variable "accessors" { default = [] }            # service-account emails
variable "required_apis" {}

locals {
  secrets_content = yamldecode(file(var.secrets_file))

  secrets = {
    for key, value in local.secrets_content :
    "${key}" => value
  }
}

resource "google_secret_manager_secret" "this" {
  for_each   = local.secrets
  project    = var.gcp_project_id
  secret_id  = each.key
  replication {
    auto {}
  }
  depends_on = [var.required_apis]
}

resource "google_secret_manager_secret_version" "this" {
  for_each    = local.secrets
  secret      = google_secret_manager_secret.this[each.key].id
  secret_data = each.value
}

resource "google_secret_manager_secret_iam_member" "accessor" {
  for_each = {
    for sa in var.accessors :
    sa => sa
  }
  project    = var.gcp_project_id
  secret_id  = google_secret_manager_secret.this["ANTHROPIC_API_KEY"].secret_id
  role       = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${each.value}"
  depends_on = [google_secret_manager_secret.this]
}

# 出力
output "secrets" {
  value = {
    for k, v in google_secret_manager_secret.this :
    k => {
      name    = v.name
      version = google_secret_manager_secret_version.this[k].name
    }
  }
}
