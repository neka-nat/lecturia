terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    prefix = "tfstate/v1"
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.primary_region
}

module "required-api" {
  source = "./modules/required-api"
}

module "artifact-registry" {
  source                     = "./modules/artifact-registry"
  gcp_project_id             = var.gcp_project_id
  artifact_registry_location = var.primary_region
  required_apis              = module.required-api.required_apis
}
