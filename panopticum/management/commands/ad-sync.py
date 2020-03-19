import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django_auth_ldap.config import LDAPSearch
from panopticum.ldap import PanopticumLDAPBackend

logger = logging.getLogger(__name__)


def fetch_users(force_group=False, group=None):
    """ Copy some behavior from django-auth-ldap login. Unfortunately django-auth-ldap library allow
     populate users only by username. But user LDAP structure can contain user foreign key with different
     value, for example DN instead username. For example LDAP attrs:
     {
        "cn=John.Doe,ou=users,dn=example,dn=com",
        "company": "Some company",
        "manager": "cn=big.boss,ou=users,dn=example,dn=com",
        ...
     }
     At this example will be all ok if "manager" = "big.boss". Also "CN" ca be different with "username".
     For resolving "manager" field we should make request to LDAP by CN, get LDAP attrs, and create
     manager django user from LDAP attrs.
     """
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

    # define connection to LDAP
    connection = backend.ldap.initialize(backend.settings.SERVER_URI, bytes_mode=False)
    if backend.settings.BIND_DN:
        connection.simple_bind_s(backend.settings.BIND_DN, backend.settings.BIND_PASSWORD)
    for opt, value in backend.settings.CONNECTION_OPTIONS.items():
        connection.set_option(opt, value)

    if backend.settings.START_TLS:
        logger.debug("Initiating TLS")
        connection.start_tls_s()

    if group:
        managers_group, _ = Group.objects.get_or_create(name=group)

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

        if group and (force_group or built):
            managers_group.user_set.add(user)

    logger.info(f'added {added} users')
    logger.info(f'updated {updated} users')


class Command(BaseCommand):
    def handle(self, **options):

        try:
            fetch_users(force_group=options.get('force_group'),
                        group=options.get('group'))
        except RuntimeError as err:
            raise CommandError(err)

    def add_arguments(self, parser):
        parser.add_argument('--force_group',
                            action='store_true',
                            help='Force adding all users to group.',
                            )
        parser.add_argument('--group',
                            default='All',
                            help='Add new users to group.',
                            )

