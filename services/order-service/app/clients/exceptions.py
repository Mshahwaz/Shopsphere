class ProductNotFoundError(Exception):
    pass


class ProductServiceUnavailableError(Exception):
    pass


class ProductServiceTimeoutError(Exception):
    pass


class ProductServiceError(Exception):
    pass

class InventoryNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class InventoryServiceUnavailableError(Exception):
    pass


class InventoryServiceTimeoutError(Exception):
    pass


class InventoryServiceError(Exception):
    pass

class PaymentNotFoundError(Exception):
    pass


class PaymentFailedError(Exception):
    pass


class PaymentServiceUnavailableError(Exception):
    pass


class PaymentServiceTimeoutError(Exception):
    pass


class PaymentServiceError(Exception):
    pass