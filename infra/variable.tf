variable "gcp_project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "primary_region" {
  description = "プライマリーリージョン"
  type        = string
}

variable "container_image" {
  description = "Artifact Registry に push 済みのアプリ用コンテナ (gcr.io/…)"
  type        = string
}

variable "public_bucket_name" {
  description = "講義データを置く公開バケット名"
  type        = string
}

variable "lecture_queue_name" {
  description = "Cloud Tasks キュー名"
  type        = string
  default     = "lecture-queue"
}

variable "secrets_file" {
  description = "Secret Manager に保存するシークレットのファイルパス"
  type        = string
  default     = "secrets.yaml"
}

variable "cors_allowed_origins" {
  description = "CORS 許可するオリジン"
  type        = string
}

variable "db_instance_name" {
  description = "Cloud SQL インスタンス名"
  type        = string
  default     = "lecturia-postgres"
}

variable "db_name" {
  description = "PostgreSQL データベース名"
  type        = string
  default     = "lecturia"
}

variable "db_user" {
  description = "PostgreSQL アプリケーションユーザー"
  type        = string
  default     = "lecturia"
}

variable "db_tier" {
  description = "Cloud SQL インスタンス tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_version" {
  description = "Cloud SQL PostgreSQL バージョン"
  type        = string
  default     = "POSTGRES_16"
}

variable "db_backup_enabled" {
  description = "Cloud SQL 自動バックアップを有効化するか"
  type        = bool
  default     = false
}

variable "db_deletion_protection" {
  description = "Cloud SQL の deletion protection"
  type        = bool
  default     = false
}
