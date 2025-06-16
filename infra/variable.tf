variable "app_container_image" {
  description = "Artifact Registry に push 済みのアプリ用コンテナ (gcr.io/…)"
  type        = string
}

variable "worker_container_image" {
  description = "Artifact Registry に push 済みのワーカー用コンテナ (gcr.io/…)"
  type        = string
}

variable "public_bucket_name" {
  description = "講義データを置く公開バケット名"
  type        = string
  default     = "lecturia-public-storage"
}

variable "anthropic_api_key" {
  description = "Anthropic API Key（Secret Manager に保存）"
  type        = string
  sensitive   = true
}

variable "brave_api_key" {
  description = "Brave Search API Key（Secret Manager に保存）"
  type        = string
  sensitive   = true
}
