from django import template
register = template.Library()

@register.filter
def prev(indexable, i):
    return indexable[i-1]

@register.filter
def last(indexable):
    return indexable[len(indexable)-1]

@register.filter
def position(tag):
    return tag.position

