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

variable "secrets_file" {
  description = "Secret Manager に保存するシークレットのファイルパス"
  type        = string
  default     = "secrets.yaml"
}
