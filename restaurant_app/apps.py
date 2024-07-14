from django.apps import AppConfig

class RestaurantAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurant_app'

    def ready(self):
        import restaurant_app.signals
