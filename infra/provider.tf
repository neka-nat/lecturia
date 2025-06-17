terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "lecturia-tfstate-dev"
    prefix = "dev"
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.primary_region
}
