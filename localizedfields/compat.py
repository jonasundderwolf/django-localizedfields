try:
    from django.utils.deconstruct import deconstructible
except ImportError:  # Django 1.7+ migrations
    deconstructible = lambda klass, *args, **kwargs: klass  # NOQA
