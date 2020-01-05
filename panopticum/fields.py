from django.db import models

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


class SigneeField(models.ForeignKey):
    def __init__(self, _title="", *args, **kwargs):
        kwargs['verbose_name'] = _title
        kwargs['on_delete'] = on_delete=models.PROTECT
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['to'] = 'panopticum.Person'
        super().__init__(*args, **kwargs)