from rest_framework import views
from rest_framework.pagination import PageNumberPagination


class DataPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return views.Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/? {page_query_param}=4'.format(
                        page_query_param=self.page_query_param
                    )
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/? {page_query_param}=2'.format(
                        page_query_param=self.page_query_param)
                },
                'page_size': {
                    'type': 'integer',
                    'example': 123,
                },
                'total_pages': {
                    'type': 'integer',
                    'example': 123,
                },
                'current_page': {
                    'type': 'integer',
                    'example': 123,
                },
                'total_results': {
                    'type': 'integer',
                    'example': 123,
                },
                'results': schema,
            },
        }
