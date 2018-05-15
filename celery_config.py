# coding: utf-8

from celery.schedules import crontab


# CELERYBEAT_SCHEDULE = {
#     'top-column-task': {
#         'task': 'lg_data.queue.tasks.top_column_task',
#         'schedule': crontab(minute=0, hour='3, 16', day_of_week='sun-mon,wed-sat'),
#     },
#     'top-column-spider-task': {
#         'task': 'lg_data.queue.tasks.top_column_spider_task',
#         'schedule': crontab(minute=0, hour='6,17', day_of_week='sun-mon,wed-sat')
#     },
#     'total-column-task': {
#         'task': 'lg_data.queue.tasks.total_column_task',
#         'schedule': crontab(minute=0, hour='1', day_of_week='tues'),
#     },
#     'total-column-spider-task': {
#         'task': 'lg_data.queue.tasks.top_column_spider_task',
#         'schedule': crontab(minute=0, hour='2', day_of_week='tues')
#     },
# }

CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_TIMEZONE = 'Asia/Shanghai'

CELERYD_CONCURRENCY = 5

CELERYD_MAX_TASKS_PER_CHILD = 300

CELERYD_FORCE_EXECV = True  # 非常重要,有些情况下可以防止死锁

CELERYD_PREFETCH_MULTIPLIER = 1
