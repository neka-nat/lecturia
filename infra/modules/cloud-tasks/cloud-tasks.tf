variable "gcp_project_id" {}
variable "location"       {}
variable "queue_name"     {}
variable "required_apis"  {}

resource "google_cloud_tasks_queue" "this" {
  name     = var.queue_name
  project  = var.gcp_project_id
  location = var.location

  depends_on = [var.required_apis]
}

output "queue_name" { value = google_cloud_tasks_queue.this.name }
