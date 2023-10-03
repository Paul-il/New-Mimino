import os
from celery import Celery
from celery.schedules import crontab
from tasks import reset_tips 

# установите переменную окружения DJANGO_SETTINGS_MODULE,
# указывающую на настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')

app = Celery('restaurant_project')

# загрузка настроек Celery из файла настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()



@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(day_of_month='1'), reset_tips.s())