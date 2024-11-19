from django.apps import AppConfig
from . import __version__

class HRApplicationsConfig(AppConfig):
    name = 'hrapplications_two'
    label = 'hrapplications_two'
    verbose_name = f"HR Tools v{__version__}"
