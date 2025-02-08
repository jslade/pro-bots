import math
import random

from ...models.game.map import Grid, Cell


class MapMaker:
    def generate(self, width: int, height: int) -> Grid:
        grid = Grid(
            width=width,
            height=height,
            cells=[Cell(x=i % width, y=int(i / width)) for i in range(width * height)],
        )

        self.randomize_crystals(grid)

        return grid

    def randomize_crystals(self, grid: Grid) -> None:
        # Very simple random distribution in some number of cells:
        total_cells = len(grid.cells)
        min_cells = int(total_cells * 0.20)
        with_crystals = random.randint(min_cells, total_cells - min_cells)

        for i in range(total_cells):
            grid.cells[i].crystals = 0

        for _ in range(with_crystals):
            x = random.randint(0, grid.width - 1)
            y = random.randint(0, grid.height - 1)
            grid.get(x, y).crystals = random.randint(5, 20)
