# Lecturia Infrastructure

## Setup

```bash
export PROJECT_ID=<your-project-id>
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud auth application-default login
```

```bash
terraform init
terraform plan
terraform apply
```

`terraform.tfvars` には `db_instance_name`, `db_name`, `db_user` などの Cloud SQL 設定を入れてください。`secrets.yaml` には既存 API key に加えて `DB_PASSWORD` も必要です。

When you finish working on the project, you can revoke the application default credentials by running the following command:

```bash
gcloud auth application-default revoke
```
