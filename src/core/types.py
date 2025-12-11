from enum import Enum, IntEnum


class PageSize(IntEnum):
    small = 20
    medium = 50
    large = 100


class PaymentType(Enum):
    cash = "cash"
    bankСard = "bank-card"
    credit = "credit"
