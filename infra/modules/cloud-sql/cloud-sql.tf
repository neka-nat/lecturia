variable "gcp_project_id" {}
variable "primary_region" {}
variable "instance_name" {}
variable "database_name" {}
variable "database_user" {}
variable "database_password" {
  sensitive = true
}
variable "database_version" {}
variable "tier" {}
variable "backup_enabled" {
  type = bool
}
variable "deletion_protection" {
  type = bool
}
variable "required_apis" {}

resource "google_sql_database_instance" "this" {
  project          = var.gcp_project_id
  name             = var.instance_name
  region           = var.primary_region
  database_version = var.database_version

  settings {
    tier = var.tier

    availability_type = "ZONAL"

    ip_configuration {
      ipv4_enabled = true
    }

    backup_configuration {
      enabled = var.backup_enabled
    }
  }

  deletion_protection = var.deletion_protection

  depends_on = [var.required_apis]
}

resource "google_sql_database" "this" {
  project  = var.gcp_project_id
  name     = var.database_name
  instance = google_sql_database_instance.this.name
}

resource "google_sql_user" "this" {
  project  = var.gcp_project_id
  name     = var.database_user
  instance = google_sql_database_instance.this.name
  password = var.database_password
}

output "instance_name" {
  value = google_sql_database_instance.this.name
}

output "connection_name" {
  value = google_sql_database_instance.this.connection_name
}

output "database_name" {
  value = google_sql_database.this.name
}

output "database_user" {
  value = google_sql_user.this.name
}
