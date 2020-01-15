from django_auth_ldap.backend import LDAPBackend, _LDAPUser, populate_user


class PanopticumLDAPBackend(LDAPBackend):
    default_settings = {
        "FOREIGNKEY_USER_ATTR_MAP": {},
        "USER_SEARCH_FIELD": "sAMAccountName",
    }

    def update_user(self, ldap_attrs):
        username = ldap_attrs.data.get(
            self.settings.USER_SEARCH_FIELD.lower())[0].lower()
        ldap_user = _LDAPUser(self, username)
        ldap_user._user_attrs = ldap_attrs
        built = not self.get_user_model().objects.filter(username=username).exists()
        ldap_user._get_or_create_user()

        return ldap_user._user, built