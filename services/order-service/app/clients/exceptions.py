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