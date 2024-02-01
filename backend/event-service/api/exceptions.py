from apiflask import HTTPError


class InvalidUseCase(HTTPError):
    status_code = 400
    message = 'Use case invalid'
