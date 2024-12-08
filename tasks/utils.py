from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class APIResponse(Response):
    def __init__(self, data=None, status_code=status.HTTP_200_OK):
        response_data = {
            'status': status_code,
            'message': 'Success' if status_code == status.HTTP_200_OK else 'Error',
            'data': data or None
        }

        super().__init__(data=response_data, status=status_code)


class PaginationAPIResponse(Response):
    def __init__(self, data=None, pagination=None, status_code=status.HTTP_200_OK):
        response_data = {
            'status': status_code,
            'message': 'Success' if status_code == status.HTTP_200_OK else 'Error',
            'pagination': pagination,
            'data': data or None
        }

        super().__init__(data=response_data, status=status_code)
