from rest_framework.exceptions import ErrorDetail


def parse_error_code():
    data={'company_code': [ErrorDetail(string='This field must be unique.', code='unique')]}
    for key in data.items():
        pass
