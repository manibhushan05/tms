from collections import OrderedDict

from django.core.paginator import InvalidPage
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import _positive_int
from rest_framework_datatables.pagination import DatatablesPageNumberPagination, DatatablesMixin
from rest_framework.response import Response


class CustomeDatatablesPaginator(DatatablesPageNumberPagination):
    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                page_size = request.query_params[self.page_size_query_param]
                if page_size == "-1":
                    return 100000
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_paginated_response(self, data):
        if not self.is_datatable_request:
            if 'http_status' in data:
                stat = data['http_status']
                data.pop('http_status')
            else:
                stat = status.HTTP_200_OK
            response = OrderedDict([
                ('count', self.page.paginator.count),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('data', data["data"]),
                ('msg', data["msg"]),
                ('status', data["status"]),
                ('status_code', data["status_code"])
            ])
            if 'summary' in data:
                response['summary'] = data['summary']
            return Response(response, status=stat)
        response=OrderedDict([
            ('recordsTotal', self.total_count),
            ('recordsFiltered', self.count),
            ('data', data["data"]),
            ('msg', data["msg"]),
            ('status', data["status"]),
            ('status_code', data["status_code"])
        ])
        if 'summary' in data:
            response['summary'] = data['summary']
        return Response(response)
