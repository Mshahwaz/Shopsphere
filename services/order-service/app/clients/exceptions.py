class ProductNotFoundError(Exception):
    pass


class ProductServiceUnavailableError(Exception):
    pass


class ProductServiceTimeoutError(Exception):
    pass


class ProductServiceError(Exception):
    pass