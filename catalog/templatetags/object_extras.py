from django import template

register = template.Library()

@register.filter
def obj_display(obj):
    return str(obj)

@register.filter
def get_drawers_as_list(obj):
    """
    Retorna los cajones de un estante como: E1- C1,C2,C3
    Solo aplica si el objeto tiene drawer_set (estante)
    """
    if hasattr(obj, "drawer_set"):
        drawers = obj.drawer_set.all().order_by('id')
        drawer_names = [d.name for d in drawers]
        return f"{obj.name}- {','.join(drawer_names)}"
    return ""  # si no tiene drawers, retorna vacío

@register.filter
def has_drawer_list(obj):
    """
    Retorna True si el objeto tiene cajones (drawer_set)
    """
    return hasattr(obj, "drawer_set") and obj.drawer_set.exists()