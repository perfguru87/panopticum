import logging

from django.core.management.base import BaseCommand, CommandError
from django_auth_ldap.config import LDAPSearch
from panopticum.ldap import PanopticumLDAPBackend

logger = logging.getLogger(__name__)


def fetch_users():
    updated = 0
    added = 0
    backend = PanopticumLDAPBackend()

    if backend.settings.REQUIRE_GROUP:
        filterstr = f'(&(objectClass=USER)(memberOf={backend.settings.REQUIRE_GROUP}))'
    else:
        filterstr = f'(objectClass=USER)'

    search = LDAPSearch(backend.settings.USER_SEARCH.base_dn,
                        backend.settings.USER_SEARCH.scope,
                        filterstr)

    connection = backend.ldap.initialize(backend.settings.SERVER_URI, bytes_mode=False)
    if backend.settings.BIND_DN:
        connection.simple_bind_s(backend.settings.BIND_DN, backend.settings.BIND_PASSWORD)
    for opt, value in backend.settings.CONNECTION_OPTIONS.items():
        connection.set_option(opt, value)

    if backend.settings.START_TLS:
        logger.debug("Initiating TLS")
        connection.start_tls_s()
    ldap_attrs = search.execute(connection)
    logger.info(f'Found {len(ldap_attrs)} entries')
    for ldap_attr in ldap_attrs:
        logger.debug(f"process {ldap_attr[1].data[backend.settings.USER_SEARCH_FIELD.lower()]}")
        user, built = backend.update_user(ldap_attr[1])
        if built:
            added += 1
            logger.info(f'Add {user.username}')
        else:
            updated += 1
            logger.info(f'Update {user.username}')

    logger.info(f'added {added} users')
    logger.info(f'updated {updated} users')


class Command(BaseCommand):
    def handle(self, **options):

        try:
            fetch_users()
        except RuntimeError as err:
            raise CommandError(err)

