from jinja2 import Environment, FileSystemLoader
from django.conf import settings


def environment(**options):
    env = Environment(
        loader=FileSystemLoader(settings.TEMPLATES[1]['DIRS']),
        **options
    )
    return env
