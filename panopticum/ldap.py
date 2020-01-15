from django_auth_ldap.backend import LDAPBackend, _LDAPUser, populate_user


class PanopticumLDAPBackend(LDAPBackend):
    default_settings = {
        "FOREIGNKEY_USER_ATTR_MAP": {},
        "USER_SEARCH_FIELD": "sAMAccountName"
    }

    def create_user(self, ldap_attrs):
        #search = django_auth_ldap.config.LDAPSearch(dn, ldap.SCOPE_BASE)
        #related_ldap_attrs = search.execute(ldap_user._get_connection())[0][1]
        username = ldap_attrs.data.get(
            self.settings.USER_SEARCH_FIELD.lower())[0]
        ldap_user = _LDAPUser(self, username)
        ldap_user._user_attrs = ldap_attrs
        ldap_user._get_or_create_user()

        field_model_instance, built = self.get_or_build_user(username,
                                                             ldap_user)
        return field_model_instance