from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary and key in dictionary:
        return dictionary[key]
    return None

@register.filter
def convenio_color(dias):
    if dias is None:
        return "#cccccc"  # gris por default
    if dias > 180:
        return "#ff4d4d"  # rojo
    elif dias > 50:
        return "#ffcc00"  # amarillo
    return "#62ec82"      # verde
