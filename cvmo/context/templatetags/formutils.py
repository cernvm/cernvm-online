from django import template
register = template.Library()

@register.filter(name='sel')
def select_replace(value, arg):
    """ Returns the selected="selected" statement when the value equals to arg """
    if value == arg:
        return 'selected=selected'
    else:
        return ""

@register.filter(name='sel_default')
def select_replace(value, arg):
    """ Returns the selected="selected" statement when the value equals to arg or if the value is missing """
    if not value:
        return 'selected=selected'
    elif value == arg:
        return 'selected=selected'
    else:
        return ""
        
@register.filter(name='chk')
def check_replace(value):
    """ Returns the checked="checked" when the value is true """
    if value:
        return 'checked=checked'
    else:
        return ""

@register.filter(name='dis')
def disable_replace(value):
    """ Returns the disabled="disabled" statement when the value equals to arg """
    if value:
        return 'disabled=disabled'
    else:
        return ""
