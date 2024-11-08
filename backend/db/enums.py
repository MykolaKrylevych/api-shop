import enum


class Status(str, enum.Enum):
    available = "AVAILABLE"
    sold_out = "SOLDOUT"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
