from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.files.base import ContentFile
import django_auth_ldap.backend
from panopticum_django import settings
from panopticum import models


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """ Create auth token at creation User """
    if created:
        Token.objects.create(user=instance)


@receiver(django_auth_ldap.backend.populate_user, sender=django_auth_ldap.backend.LDAPBackend)
def add_photo(sender, instance=None, created=False, user=None, ldap_user=None, **kwargs):
    """ Download and assign user photo at user population from LDAP """
    ldap_field_name = settings.LDAP_USER_ATTR_MAP.get("photo")

    if ldap_field_name and ldap_user.attrs.data[ldap_field_name] and not user.photo:
        user.photo.save(name=f'{user.username}.jpg',
                        content=ContentFile(ldap_user.attrs.data[ldap_field_name][0]))

@receiver(django_auth_ldap.backend.populate_user, sender=django_auth_ldap.backend.LDAPBackend)
def update_user_foreign_keys(sender, instance=None, created=False, user=None, ldap_user=None, **kwargs):
    for model_field_name, val in settings.LDAP_USER_ATTR_MAP.items():
        search_field = "name"
        if isinstance(val, dict):
            ldap_field_name = val['ldapFieldName']
            search_field = val.get("searchField", search_field)
        else:
            ldap_field_name = val

        if ldap_user.attrs.data[ldap_field_name]:
            field_model = getattr(models.User, model_field_name).field.related_model
            if not field_model:
                continue
            field_model_instance = field_model.objects.get_or_create(**{
                search_field:ldap_user.attrs.data[ldap_field_name][0]
            })[0]
            setattr(user, model_field_name, field_model_instance)
