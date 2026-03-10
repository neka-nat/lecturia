module "required-api" {
  source = "./modules/required-api"
}

module "service_accounts" {
  source         = "./modules/service-accounts"
  gcp_project_id = var.gcp_project_id
  required_apis  = module.required-api.required_apis
}

module "artifact-registry" {
  source         = "./modules/artifact-registry"
  gcp_project_id = var.gcp_project_id
  primary_region = var.primary_region
  repository_id  = var.container_image
  required_apis  = module.required-api.required_apis
}

module "storage" {
  source               = "./modules/storage"
  gcp_project_id       = var.gcp_project_id
  primary_region       = var.primary_region
  bucket_name          = var.public_bucket_name
  public_read          = true
  cors_allowed_origins = split(",", var.cors_allowed_origins)
  required_apis        = module.required-api.required_apis
  writer_sa_email      = module.service_accounts.worker_sa_email
}

module "secret_manager" {
  source         = "./modules/secret-manager"
  gcp_project_id = var.gcp_project_id
  secrets_file   = var.secrets_file
  accessors = [
    module.service_accounts.app_sa_email,
    module.service_accounts.worker_sa_email,
  ]
  required_apis = module.required-api.required_apis
}

module "cloud_sql" {
  source              = "./modules/cloud-sql"
  gcp_project_id      = var.gcp_project_id
  primary_region      = var.primary_region
  instance_name       = var.db_instance_name
  database_name       = var.db_name
  database_user       = var.db_user
  database_password   = module.secret_manager.secret_values["DB_PASSWORD"]
  database_version    = var.db_version
  tier                = var.db_tier
  backup_enabled      = var.db_backup_enabled
  deletion_protection = var.db_deletion_protection
  required_apis       = module.required-api.required_apis
}

module "cloud_tasks" {
  source         = "./modules/cloud-tasks"
  gcp_project_id = var.gcp_project_id
  location       = var.primary_region
  queue_name     = var.lecture_queue_name
  required_apis  = module.required-api.required_apis
}

module "cloud_run_app" {
  source                = "./modules/cloud-run"
  gcp_project_id        = var.gcp_project_id
  name                  = "lecturia-app"
  primary_region        = var.primary_region
  repository_url        = module.artifact-registry.repository_url
  service_account_email = module.service_accounts.app_sa_email
  command               = "fastapi"
  args                  = ["run", "src/lecturia/server.py", "--port", "8080"]
  env = {
    GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME = var.public_bucket_name
    GOOGLE_CLOUD_PROJECT                    = var.gcp_project_id
    GOOGLE_CLOUD_LOCATION                   = var.primary_region
    LECTURIA_WORKER_URL                     = module.cloud_run_worker.url
    CORS_ALLOWED_ORIGINS                    = var.cors_allowed_origins
    DB_NAME                                 = module.cloud_sql.database_name
    DB_USER                                 = module.cloud_sql.database_user
    INSTANCE_UNIX_SOCKET                    = "/cloudsql/${module.cloud_sql.connection_name}"
  }
  secret_env = {
    "DB_PASS" = {
      secret  = module.secret_manager.secrets["DB_PASSWORD"].secret_id
      version = module.secret_manager.secrets["DB_PASSWORD"].version
    }
  }
  cloud_sql_instances = [module.cloud_sql.connection_name]
  public_access       = true
  required_apis       = module.required-api.required_apis
}

module "cloud_run_worker" {
  source                = "./modules/cloud-run"
  gcp_project_id        = var.gcp_project_id
  name                  = "lecturia-worker"
  primary_region        = var.primary_region
  repository_url        = module.artifact-registry.repository_url
  service_account_email = module.service_accounts.worker_sa_email
  command               = "fastapi"
  args                  = ["run", "src/lecturia/cloud_pipeline/workflow.py", "--port", "8080"]
  env = {
    GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME = var.public_bucket_name
    GOOGLE_CLOUD_PROJECT                    = var.gcp_project_id
    GOOGLE_CLOUD_LOCATION                   = var.primary_region
    DB_NAME                                 = module.cloud_sql.database_name
    DB_USER                                 = module.cloud_sql.database_user
    INSTANCE_UNIX_SOCKET                    = "/cloudsql/${module.cloud_sql.connection_name}"
  }
  secret_env = {
    "ANTHROPIC_API_KEY" = {
      secret  = module.secret_manager.secrets["ANTHROPIC_API_KEY"].secret_id
      version = module.secret_manager.secrets["ANTHROPIC_API_KEY"].version
    }
    "GOOGLE_API_KEY" = {
      secret  = module.secret_manager.secrets["GOOGLE_API_KEY"].secret_id
      version = module.secret_manager.secrets["GOOGLE_API_KEY"].version
    }
    "BRAVE_API_KEY" = {
      secret  = module.secret_manager.secrets["BRAVE_API_KEY"].secret_id
      version = module.secret_manager.secrets["BRAVE_API_KEY"].version
    }
    "DB_PASS" = {
      secret  = module.secret_manager.secrets["DB_PASSWORD"].secret_id
      version = module.secret_manager.secrets["DB_PASSWORD"].version
    }
  }
  cloud_sql_instances = [module.cloud_sql.connection_name]
  public_access       = true
  required_apis       = module.required-api.required_apis
}
