import re

import ldap
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_auth_ldap.config import LDAPSearch
from rest_framework.authtoken.models import Token
from django.core.files.base import ContentFile
import django_auth_ldap.backend
from panopticum_django import settings
from django.core.exceptions import ObjectDoesNotExist


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
    backend = django_auth_ldap.backend.LDAPBackend()
    for model_field_name, val in settings.LDAP_USER_ATTR_MAP.items():
        search_field = "name"
        create = True

        if isinstance(val, dict):
            ldap_field_name = val['ldapFieldName']
            search_field = val.get("searchField", search_field)
            create = val.get("create", create)
        else:
            ldap_field_name = val

        if ldap_field_name not in ldap_user.attrs.data:
            continue
        ldap_value = ldap_user.attrs.data[ldap_field_name][0]
        if not ldap_value:
            continue
        field_model = getattr(backend.get_user_model(), model_field_name).field.related_model
        if not field_model:
            continue

        if create:
            if issubclass(field_model, backend.get_user_model()) \
                    and not backend.get_user_model().objects.filter(dn=ldap_value).exists():
                search = LDAPSearch(ldap_value, ldap.SCOPE_BASE)
                related_ldap_attrs = search.execute(ldap_user._get_connection())[0][1]
                related_username = related_ldap_attrs.data.get(settings.AUTH_LDAP_USER_SEARCH_FIELD)[0]
                related_ldap_user = django_auth_ldap.backend._LDAPUser(backend, related_username)
                related_ldap_user._user_attrs = related_ldap_attrs
                related_ldap_user._get_or_create_user()

                field_model_instance, built = backend.get_or_build_user(related_username,
                                                                        related_ldap_user)
            else:
                field_model_instance = field_model.objects.get_or_create(**{
                    search_field: ldap_value
                })[0]
        else:
            try:
                field_model_instance = field_model.objects.get(**{
                    search_field: ldap_value
                })
            except ObjectDoesNotExist:
                continue

        setattr(user, model_field_name, field_model_instance)
