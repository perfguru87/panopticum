import rest_framework.response
from rest_framework.pagination import LimitOffsetPagination

class CustomPagination(LimitOffsetPagination):

    def get_next(self):
        if self.offset + self.limit >= self.count:
            return None

        offset = self.offset + self.limit
        return offset

    def get_previous(self):
        if self.offset <= 0:
            return None

        if self.offset - self.limit <= 0:
            return

        offset = self.offset - self.limit
        return offset

    def get_paginated_response(self, data):
        return rest_framework.response.Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'next': self.get_next(),
            'previous': self.get_previous(),
            'count': self.count,
            'results': data
        })