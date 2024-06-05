# your_app_name/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("Your password must contain at least %(min_length)d characters.") % {'min_length': self.min_length}

class NumericValidator:
    def validate(self, password, user=None):
        if not re.findall(r'\d', password):
            raise ValidationError(
                _("This password must contain at least one numeric character."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _("Your password must contain at least one numeric character.")

class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not re.findall(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("This password must contain at least one special character."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _("Your password must contain at least one special character.")
