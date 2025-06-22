from lecturia.storage import ls_public_bucket, is_exists_in_public_bucket
from lecturia.firestore import TaskStatus


lecture_ids = ls_public_bucket("lectures")

for lecture_id in lecture_ids:
    has_events = is_exists_in_public_bucket(f"lectures/{lecture_id}/events.json")
    task_status = TaskStatus(
        id=lecture_id,
        status="completed" if has_events else "pending",
    )
    task_status.save()
    print(f"lecture_id {lecture_id} is saved")
