from celery.signals import worker_ready
import os

# Startup tasks
@worker_ready.connect
def at_start(sender, **k):
    if os.environ.get("PLAYGROUND_ENABLED", "True") != "True":
        return
    with sender.app.connection() as conn:
         sender.app.send_task('space.tasks.create_playground', connection=conn)