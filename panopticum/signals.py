import ldap
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_auth_ldap.config import LDAPSearch
from rest_framework.authtoken.models import Token
from django.core.files.base import ContentFile
import panopticum.ldap
from panopticum_django import settings
from django.core.exceptions import ObjectDoesNotExist


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """ Create auth token at creation User """
    if created:
        Token.objects.create(user=instance)


@receiver(panopticum.ldap.populate_user, sender=panopticum.ldap.PanopticumLDAPBackend)
def add_photo(sender, instance=None, created=False, user=None, ldap_user=None, **kwargs):
    """ Download and assign user photo at user population from LDAP """
    backend = panopticum.ldap.PanopticumLDAPBackend()
    ldap_field_name = backend.settings.FOREIGNKEY_USER_ATTR_MAP.get("photo")

    if ldap_field_name and ldap_field_name in ldap_user.attrs.data and not user.photo:
        user.photo.save(name=f'{user.username}.jpg',
                        content=ContentFile(ldap_user.attrs.data[ldap_field_name][0]))


@receiver(panopticum.ldap.populate_user, sender=panopticum.ldap.PanopticumLDAPBackend)
def update_user_foreign_keys(sender, instance=None, created=False, user=None, ldap_user=None, **kwargs):
    backend = panopticum.ldap.PanopticumLDAPBackend()
    for model_field_name, val in backend.settings.FOREIGNKEY_USER_ATTR_MAP.items():
        model_search_field = "name"
        create = True

        # handle custom settings like:
        #"manager": {
        #   "searchField": "dn",
        #   "ldapFieldName": "manager",
        #   "create": False, # doesn't create object if it not exist
        #}
        if isinstance(val, dict):
            ldap_field_name = val['ldapFieldName']
            model_search_field = val.get("searchField", model_search_field)
            create = val.get("create", create)
        else:
            ldap_field_name = val

        if ldap_field_name not in ldap_user.attrs.data:
            continue
        ldap_value = ldap_user.attrs.data[ldap_field_name][0]
        if not ldap_value:
            continue
        # get model from models.Field object
        field_model = getattr(backend.get_user_model(), model_field_name).field.related_model
        if not field_model:
            continue

        if create:
            if issubclass(field_model, backend.get_user_model()) \
                    and not backend.get_user_model().objects.filter(**{model_search_field:ldap_value}).exists():
                # make raw request to LDAP for getting raw LDAP attrs
                search = LDAPSearch(ldap_value, ldap.SCOPE_BASE)
                related_ldap_attrs = search.execute(ldap_user._get_connection())[0][1]
                field_model_instance, _ = backend.update_user(related_ldap_attrs)
            else:
                # Example: models.User.get_or_create('dn=...')
                field_model_instance = field_model.objects.get_or_create(**{
                    model_search_field: ldap_value
                })[0]
        else:
            try:
                field_model_instance = field_model.objects.get(**{
                    model_search_field: ldap_value
                })
            except ObjectDoesNotExist:
                continue

        # Example: loggedin_user.manager = models.User(dn="cn=John.Doe,ou=users,dn=example,dn=com")
        setattr(user, model_field_name, field_model_instance)
