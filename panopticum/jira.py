from django.conf import settings

import http.client

import jira
import scalpl
import os


class JiraProxy:
    """
    Very simple JIRA issues proxy with fields filtering
    """

    def __init__(self):
        if os.environ.get('JIRA_URL'):
            self._jira = jira.JIRA(os.environ.get('JIRA_URL'), auth=(os.environ.get('JIRA_USER'), os.environ.get('JIRA_PASSWORD')))
        else:
            self._jira = None

    def get_issue(self, issue_key):
        if self._jira is None:
            return {'error': 'JIRA url is not configured'}, False, 500

        try:
            ji = self._jira.issue(issue_key)
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
