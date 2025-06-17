module "required-api" {
  source = "./modules/required-api"
}

module "service_accounts" {
  source          = "./modules/service-accounts"
  gcp_project_id  = var.gcp_project_id
  required_apis   = module.required-api.required_apis
}

module "storage" {
  source              = "./modules/storage"
  gcp_project_id      = var.gcp_project_id
  bucket_name         = var.public_bucket_name
  public_read         = true
  required_apis       = module.required-api.required_apis
}

module "secret_manager" {
  source          = "./modules/secret-manager"
  gcp_project_id  = var.gcp_project_id
  secrets = {
    "ANTHROPIC_API_KEY" = var.anthropic_api_key
    "BRAVE_API_KEY"     = var.brave_api_key
  }
  accessors = [
    module.service_accounts.app_sa_email,
    module.service_accounts.worker_sa_email,
  ]
  required_apis = module.required-api.required_apis
}

module "firestore" {
  source         = "./modules/firestore"
  gcp_project_id = var.gcp_project_id
  required_apis  = module.required-api.required_apis
}

module "cloud_run_app" {
  source                 = "./modules/cloud-run"
  name                   = "lecturia-app"
  location               = var.primary_region
  image                  = var.app_container_image
  service_account_email  = module.service_accounts.app_sa_email
  env                    = {
    GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME = var.public_bucket_name
    GOOGLE_CLOUD_LOCATION                   = var.primary_region
    WORKER_URL                              = module.cloud_run_worker.url
  }
  secret_env = {
    "ANTHROPIC_API_KEY" = module.secret_manager.secrets["ANTHROPIC_API_KEY"].version
    "BRAVE_API_KEY"     = module.secret_manager.secrets["BRAVE_API_KEY"].version
  }
  public_access = true
  required_apis = module.required-api.required_apis
}

module "cloud_run_worker" {
  source                 = "./modules/cloud-run"
  name                   = "lecturia-worker"
  location               = var.primary_region
  image                  = var.worker_container_image
  service_account_email  = module.service_accounts.worker_sa_email
  env                    = {
    GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME = var.public_bucket_name
    GOOGLE_CLOUD_LOCATION                   = var.primary_region
  }
  secret_env = {
    "ANTHROPIC_API_KEY" = module.secret_manager.secrets["ANTHROPIC_API_KEY"].version
    "BRAVE_API_KEY"     = module.secret_manager.secrets["BRAVE_API_KEY"].version
  }
  public_access = false
  required_apis = module.required-api.required_apis
}
