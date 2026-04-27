from django import template
from django.templatetags.static import static


register = template.Library()


@register.simple_tag
def avatar_url(user):
    if user and user.avatar:
        if user.avatar.name == 'avatar.svg':
            return static('images/avatar.svg')
        try:
            return user.avatar.url
        except ValueError:
            pass
    return static('images/avatar.svg')
