from django import template
register = template.Library()


@register.filter(name="mttb")
def message_tag_to_bootstrap(value):
    """
    Message tag to bootstrap.
    Converts messages tags into bootstrap classe
    """
    if value == "info":
        return "alert-info"
    elif value == "success":
        return "alert-success"
    elif value == "warning":
        return "alert-warning"
    elif value == "error":
        return "alert-danger"
    else:
        return "alert-info"
