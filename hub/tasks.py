from celery.signals import worker_ready

# Startup tasks
@worker_ready.connect
def at_start(sender, **k):
    with sender.app.connection() as conn:
         sender.app.send_task('space.tasks.create_playground', connection=conn)