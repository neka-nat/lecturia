from diagrams import Diagram, Cluster, Edge
from diagrams.gcp.compute import Run
from diagrams.gcp.devtools import ContainerRegistry, Tasks
from diagrams.gcp.database import Firestore
from diagrams.gcp.storage import Storage
from diagrams.gcp.security import KeyManagementService, Iam


with Diagram("Lecturia – GCP Architecture", filename="lecturia_arch", show=False):
    # 共通 IAM (サービスアカウント)
    sa = Iam("service-account")

    # Artifact Registry（Container Registry アイコンで代用）
    ar = ContainerRegistry("artifact-registry")

    # Secret Manager（KMS アイコンで代用）
    secrets = KeyManagementService("secret-manager")

    # Cloud Storage（公開バケット）
    gcs_public = Storage("lecturia-public-storage")

    # Firestore
    firestore = Firestore("firestore")

    with Cluster("Cloud Run"):
        cloud_run_app    = Run("lecturia-api\n(front)")
        cloud_run_worker = Run("lecturia-worker\n(pipeline)")

    # Cloud Tasks
    tasks = Tasks("cloud-tasks")

    # ── リレーション ────────────────────────────────
    # フロント API → Worker への非同期実行
    cloud_run_app >> Edge(label="create task") >> tasks >> Edge(label="push JSON") >> cloud_run_worker

    # Worker が Artifact Registry からコンテナ取得
    ar >> cloud_run_worker

    # Worker が Secret Manager から APIキー参照
    secrets >> cloud_run_worker

    # Cloud Run サービスが Firestore & GCS を利用
    cloud_run_worker >> firestore
    cloud_run_worker >> gcs_public

    # フロント API も読み取りでストレージ参照
    cloud_run_app >> gcs_public

    # すべての Cloud Run サービスは同一 Service Account を使用
    sa >> [cloud_run_app, cloud_run_worker]
