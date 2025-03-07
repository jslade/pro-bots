from dataclasses import dataclass
from typing import Callable, ClassVar, Optional, Self

from ..mixins.pydantic_base import BaseSchema


class Cell(BaseSchema):
    MAX_CRYSTALS: ClassVar[int] = 1000

    x: int
    y: int
    crystals: int = 0


class Grid(BaseSchema):
    width: int
    height: int
    cells: list[Cell]

    def get(self, x: int, y: int) -> Cell:
        if x < 0 or x >= self.width:
            raise ValueError("x out of bounds")

        if y < 0 or y >= self.height:
            raise ValueError("y out of bounds")

        return self.cells[y * self.width + x]

    def to_str(self, decorator: Optional[Callable[[Cell, str], str]] = None) -> str:
        x_vals = [" {:2d} ".format(x) for x in range(self.width)]
        row_sep = "   +" + "+".join(["----" for x in range(self.width)]) + "+"

        s = []
        s.append(row_sep)

        def c_str(x: int, y: int) -> str:
            cell = self.get(x, y)
            s = " {:2d} ".format(cell.crystals) if cell.crystals else "    "
            if decorator:
                s = decorator(cell, s)
            return s

        for y in range(self.height - 1, -1, -1):
            c_vals = [c_str(x, y) for x in range(self.width)]
            s.append("{:2d}".format(y) + " |" + "|".join(c_vals) + "|")
            s.append(row_sep)

        s.append("    " + " ".join(x_vals))
        return "\n".join(s)

    @classmethod
    def blank(cls, width: int, height: int) -> Self:
        return cls(
            width=width,
            height=height,
            cells=[Cell(x=i % width, y=int(i / width)) for i in range(width * height)],
        )
