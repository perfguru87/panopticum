from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.files.base import ContentFile
import django_auth_ldap.backend


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """ Create auth token at creation User """
    if created:
        Token.objects.create(user=instance)


@receiver(django_auth_ldap.backend.populate_user, sender=django_auth_ldap.backend.LDAPBackend)
def add_photo(sender, instance=None, created=False, user=None, ldap_user=None, **kwargs):
    """ Download and assign user photo at user population from LDAP """
    if ldap_user.attrs.data['thumbnailphoto'] and not user.photo:
        user.photo.save(name=f'{user.username}.jpg',
                        content=ContentFile(ldap_user.attrs.data['thumbnailphoto'][0]))
