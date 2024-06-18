from celery import shared_task
from restaurant_app.views_folder.tip_view import Tip

@shared_task
def reset_tips():
    Tip.objects.update(amount=0)
