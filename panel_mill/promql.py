from typing import Self


class LabelFilters:
    def __init__(self, *filters: str):
        self.filters = list(filters)

    def __str__(self):
        return "{{{}}}".format(", ".join(self.filters))

    def __add__(self, other: str | Self):
        if isinstance(other, str):
            return LabelFilters(*self.filters, other)
        return LabelFilters(*self.filters, *other.filters)
