from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSerPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        next_link = ""
        previous_link = ""

        if self.get_next_link() is not None:
            next_link = self.get_next_link()
        if self.get_previous_link() is not None:
            previous_link = self.get_previous_link()

        page_count = self.page.paginator.count // self.page_size
        if self.page.paginator.count % self.page_size != 0:
            page_count = self.page.paginator.count // self.page_size + 1
        return Response({
            'links': {
                'next': next_link,
                'previous': previous_link,
            },
            'meta': {
                'current_page': self.page.number,  # сейчас
                'page_count': page_count,
                'pre_page': self.page_size,  # кол эл на странице
                'total_count': self.page.paginator.count,
            },
            'results': data
        })


class MeetingsPagination(PageNumberPagination):
    PAGE_SIZE = 2
    page_size_query_param = 'page_size'

    max_page_size = 1000

    def get_paginated_response(self, data):
        next_link = ""
        previous_link = ""

        if self.get_next_link() is not None:
            next_link = self.get_next_link()
        if self.get_previous_link() is not None:
            previous_link = self.get_previous_link()

        page_count = self.page.paginator.count // self.PAGE_SIZE
        if self.page.paginator.count % self.PAGE_SIZE != 0:
            page_count = self.page.paginator.count // self.PAGE_SIZE + 1
        return Response({
            'links': {
                'next': next_link,
                'previous': previous_link,
            },
            'meta': {
                'current_page':  self.page.number,  # сейчас
                'page_count': page_count,
                'pre_page': self.PAGE_SIZE,  # кол эл на странице
                'total_count': self.page.paginator.count,
            },
            'results': data
        })


class MeetingProfilesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):

        next_link = ""
        previous_link = ""

        if self.get_next_link() is not None:
            next_link = self.get_next_link()
        if self.get_previous_link() is not None:
            previous_link = self.get_previous_link()

        page_count = self.page.paginator.count // self.page_size
        if self.page.paginator.count % self.page_size != 0:
            page_count = self.page.paginator.count // self.page_size + 1
        return Response({
            'links': {
                'next': next_link,
                'previous': previous_link,
            },
            'meta': {
                'current_page': self.page.number,  # сейчас
                'page_count': page_count,
                'pre_page': self.page_size,  # кол эл на странице
                'total_count': self.page.paginator.count,
            },
            'results': data
        })

