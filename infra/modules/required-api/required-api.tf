resource "google_project_service" "required_apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false  # destroyで消去しない
}