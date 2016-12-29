from django import template
import django
import os, re

register = template.Library()


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, 'version_gen.py')).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_contributors():
    """Return contributors listed in `CONTRIBUTORS.txt`."""
    try:
        contr_file = open(os.path.join('CONTRIBUTORS.txt')).read()
        return contr_file
    except IOError:
        pass



@register.simple_tag
def version_number():
    return get_version('projects_helper/apps')

@register.simple_tag
def contributors():
    return get_contributors()

@register.simple_tag
def django_version():
    return django.get_version()
