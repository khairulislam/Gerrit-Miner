from enum import Enum


class Status(Enum):
    abandoned, closed, merged, new, open, pending = range(6)

    def __str__(self):
        return f"{self.name}"
