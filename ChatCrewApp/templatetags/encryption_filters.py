from django import template
from ..utils import encrypt as encrypt_util  # Avoid naming conflict

register = template.Library()

@register.filter
def encrypt(value):
    return encrypt_util(value)
