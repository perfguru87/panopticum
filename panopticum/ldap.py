from django_auth_ldap.backend import LDAPBackend, _LDAPUser, populate_user


class PanopticumLDAPBackend(LDAPBackend):
    """ Custom LDAP backend with panopticum specific behavior """

    default_settings = {
        # Object relation map for adding foreign key objects like AUTH_LDAP_USER_ATTR_MAP.
        # key is foreignKey field at django model
        # value is LDAP field
        # For example:
        # "FOREIGNKEY_USER_ATTR_MAP": {
        #     "department": "department",
        #     "manager": {
        #         "searchField": "dn", # override model field for matching between model and LDAP entry.
                                       # by default it is "name". But sometimes LDAP value it's not model "name".
        #         "ldapFieldName": "manager" # is same to "department" in previous entry
        #     }
        #}
        "FOREIGNKEY_USER_ATTR_MAP": {},
        # What LDAP field we should use for matching users.
        "USER_SEARCH_FIELD": "sAMAccountName",
    }

    def update_user(self, ldap_attrs):
        """ Create or update model User from LDAP data. django-auth-ldap library doesn't allow to
         populate user from raw LDAP data. Only by username. Sometimes we doesn't know username, but know
         other criteria, etc. DN. We should make LDAP request by DN, get LDAP data and create User model entry """
        username = ldap_attrs.data.get(
            self.settings.USER_SEARCH_FIELD.lower())[0].lower()
        ldap_user = _LDAPUser(self, username)
        ldap_user._user_attrs = ldap_attrs
        built = not self.get_user_model().objects.filter(username=username).exists()
        ldap_user._get_or_create_user()

        return ldap_user._user, built