from django.db import models
import django.forms

# TODO: can we remove that?
NO_PARTIAL_YES = (
    ('unknown', "?"),
    ('n/a', "N/A"),
    ('no', "No"),
    ('partial', "Partial"),
    ('yes', "Yes")
)

LOW_MED_HIGH = (
    ('unknown', "?"),
    ('n/a', "N/A"),
    ('none', "None"),
    ('low', "Low"),
    ('med', "Med"),
    ('high', "High")
)


# TODO: can we remove that field?
class NoPartialYesField(models.CharField):
    def __init__(self, _title="", *args, **kwargs):
        kwargs['verbose_name'] = _title
        kwargs['max_length'] = 16
        kwargs['choices'] = NO_PARTIAL_YES
        kwargs['default'] = kwargs['choices'][0][0]
        super().__init__(*args, **kwargs)


class LowMedHighField(models.CharField):
    def __init__(self, _title="", *args, **kwargs):
        kwargs['verbose_name'] = _title
        kwargs['max_length'] = 16
        kwargs['choices'] = LOW_MED_HIGH
        kwargs['default'] = kwargs['choices'][0][0]
        super().__init__(*args, **kwargs)


class SmartTextField(models.TextField):
    # FIXME: store arbitrary comments and replace JIRA items and URLs by links
    def __init__(self, _title="", *args, **kwargs):
        # FIXME: store array of URLs (e.g. "|"-separated)
        kwargs['verbose_name'] = _title
        kwargs['default'] = ""
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)

# TODO: can we remove that field?
class SigneeField(models.ForeignKey):
    def __init__(self, _title="", *args, **kwargs):
        kwargs['verbose_name'] = _title
        kwargs['on_delete'] = models.PROTECT
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['to'] = 'panopticum.User'
        super().__init__(*args, **kwargs)


class RequirementChoiceField(django.forms.ModelChoiceField):
    """ custom field for pretty presentation of Requirement model at django admin. It's same by
    to override __str__ method by model, but affected only django admin panel.
    """
    def label_from_instance(self, obj):
        return f"{obj.title}"

class RequirementStatusChoiceField(django.forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}"
