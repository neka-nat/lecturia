# Lecturia Infrastructure

## Setup

```bash
export PROJECT_ID=<your-project-id>
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud auth application-default login
```



When you finish working on the project, you can revoke the application default credentials by running the following command:

```bash
gcloud auth application-default revoke
```