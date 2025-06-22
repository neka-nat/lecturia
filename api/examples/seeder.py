from lecturia.storage import ls_public_bucket
from lecturia.firestore import TaskStatus


lecture_ids = ls_public_bucket("lectures")

for lecture_id in lecture_ids:
    task_status = TaskStatus(
        id=lecture_id,
        status="completed",
    )
    task_status.save()
    print(f"lecture_id {lecture_id} is saved")
