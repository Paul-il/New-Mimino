from celery import shared_task
from ..models.tables import Tip

@shared_task
def reset_tips():
    Tip.objects.update(amount=0)
