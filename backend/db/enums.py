import enum


class Status(str, enum.Enum):
    available = "AVAILABLE"
    sold_out = "SOLDOUT"
