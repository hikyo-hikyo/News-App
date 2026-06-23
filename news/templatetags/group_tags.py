# news/templatetags/group_tags.py
from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if a user belongs to a specific group"""
    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()
    return False


@register.filter(name='has_any_group')
def has_any_group(user, group_names):
    """Check if user belongs to any of the groups (comma separated string)"""
    if not user.is_authenticated:
        return False

    # Split string like "Journalist,Editor" into list
    groups_list = [group.strip() for group in group_names.split(',')]
    return user.groups.filter(name__in=groups_list).exists()
