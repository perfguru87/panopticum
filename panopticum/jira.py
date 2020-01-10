from django.conf import settings

import http.client

import jira
import scalpl


class JiraProxy:
    """
    Very simple and stupid JIRA issues proxy with fields filtering
    """

    def __init__(self):
        self.jira = jira.JIRA(settings.JIRA_CONFIG['URL'], auth=(settings.JIRA_CONFIG['USER'], settings.JIRA_CONFIG['PASSWORD']))

    def get_issue(self, issue_key):
        try:
            ji = self.jira.issue(issue_key)
        except jira.exceptions.JIRAError as e:
            return {'error': str(e.text)}, False, e.status_code

        j_from = scalpl.Cut(ji.raw)
        j_to = scalpl.Cut({})

        ar = [f['name'] for f in j_from['fields.fixVersions']]
        j_from.update({'fields.fixVersionsStr': ", ".join(ar)})

        ar = [f['name'] for f in j_from['fields.components']]
        j_from.update({'fields.componentsStr': ", ".join(ar)})

        for field in ['key',
                      'fields.summary',
                      'fields.created',
                      'fields.priority.name',
                      'fields.priority.iconUrl',
                      'fields.issuetype.name',
                      'fields.issuetype.iconUrl',
                      'fields.fixVersionsStr',
                      'fields.status.name',
                      'fields.assignee.name',
                      'fields.componentsStr',
                      'fields.resolution',
                      'fields.resolutiondate']:

            tokens = field.split('.')
            for n in range(0, len(tokens)):
                token = ".".join(tokens[0:n])
                if token and token not in j_to:
                    j_to.update({token: {}})

            j_to.update({field: j_from[field]})

        return {'results': j_to.data}, False, http.client.OK
