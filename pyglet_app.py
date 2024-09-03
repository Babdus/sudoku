import sys

import pyglet
from sudoku import Sudoku
from pyglet.window import key

colors = {
    'white': (255, 255, 255),
    'ash': (239, 239, 239),
    'lemon': (255, 255, 223),
    'scarlet': (255, 191, 191),
    'ruby': (239, 175, 175),
    'orange': (255, 223, 191),
    'stone': (127, 127, 127),
    'black': (0, 0, 0),
    'lime': (223, 255, 191),
    'moss': (207, 239, 175),
    'olive': (239, 255, 207),
    'lilac': (255, 191, 255),
    'mauve': (239, 175, 239),
    'peach': (255, 207, 239)
}


class Game:
    def __init__(self, num=3, fraction=0.5, grid_width=720, margin=20):
        self.grid_width = (grid_width // (num ** 2)) * (num ** 2)
        self.margin = margin
        self.window = pyglet.window.Window(
            self.grid_width + self.margin * 2,
            self.grid_width + self.margin * 2)
        self.on_draw = self.window.event(self.on_draw)
        self.on_mouse_press = self.window.event(self.on_mouse_press)
        self.on_key_press = self.window.event(self.on_key_press)

        self.total_symbols = [chr(i) for i in range(49, 58)] + [chr(i) for i in range(97, 123)]
        self.num = num
        self.cell_width = self.grid_width // (self.num ** 2)

        self.canvas = pyglet.shapes.Rectangle(
            x=0,
            y=0,
            width=self.window.width,
            height=self.window.height,
            color=colors['white']
        )
        self.grid_batch = pyglet.graphics.Batch()
        self.fixed_cells_batch = pyglet.graphics.Batch()

        self.grid_background_group = pyglet.graphics.Group(order=0)
        self.grid_mid_ground_group = pyglet.graphics.Group(order=1)
        self.grid_foreground_group = pyglet.graphics.Group(order=2)

        self.sudoku = Sudoku(self.num, self.total_symbols)
        self.sudoku.randomize_grid()
        self.sudoku.randomize_fixed_cells(fraction=fraction)

        self.gridlines = []
        self.create_grid()
        self.create_gridlines()

        pyglet.app.run()

    def create_grid(self):
        for i in range(self.num ** 2):
            for j in range(self.num ** 2):
                x = self.cell_width * (j + 0.5) + self.margin
                y = self.cell_width * (i + 0.5) + self.margin

                if self.sudoku.fixed_cells[i][j]:
                    color = colors['ash']
                else:
                    color = colors['white']
                square = pyglet.shapes.Rectangle(
                    x=x,
                    y=y,
                    width=self.cell_width,
                    height=self.cell_width,
                    color=color,
                    batch=self.grid_batch,
                    group=self.grid_background_group
                )
                square.anchor_x = self.cell_width // 2
                square.anchor_y = self.cell_width // 2

                label = pyglet.text.Label(
                    self.sudoku.grid[i][j],
                    font_name='Arial',
                    font_size=self.cell_width // 3,
                    bold=True,
                    x=x,
                    y=y,
                    anchor_x='center',
                    anchor_y='center',
                    color=colors['black'],
                    batch=self.fixed_cells_batch
                )
                self.sudoku.cells[i][j]['square'] = square
                self.sudoku.cells[i][j]['label'] = label

    def create_gridlines(self):
        for i in range(0, self.num ** 2 + 1):
            if i % self.num == 0:
                width = 6
                if i == 0 or i == self.num ** 2:
                    color = colors['black']
                    group = self.grid_foreground_group
                else:
                    color = colors['stone']
                    group = self.grid_mid_ground_group
            else:
                width = 2
                color = colors['stone']
                group = self.grid_mid_ground_group

            vertical_line = pyglet.shapes.Rectangle(
                x=i * self.cell_width + self.margin,
                y=self.grid_width // 2 + self.margin,
                width=width,
                height=self.grid_width + width - 2,
                color=color,
                batch=self.grid_batch,
                group=group
            )
            vertical_line.anchor_x = width // 2
            vertical_line.anchor_y = (self.grid_width + width - 2) // 2

            horizontal_line = pyglet.shapes.Rectangle(
                x=self.grid_width // 2 + self.margin,
                y=i * self.cell_width + self.margin,
                width=self.grid_width + width - 2,
                height=width,
                color=color,
                batch=self.grid_batch,
                group=group
            )
            horizontal_line.anchor_x = (self.grid_width + width - 2) // 2
            horizontal_line.anchor_y = width // 2

            self.gridlines.append(vertical_line)
            self.gridlines.append(horizontal_line)

    def on_draw(self):
        self.window.clear()

        if self.sudoku.win or self.sudoku.double_win:
            for i in range(self.num ** 2):
                for j in range(self.num ** 2):
                    if self.sudoku.fixed_cells[i][j]:
                        if self.sudoku.double_win:
                            color = colors['mauve']
                        else:
                            color = colors['moss']
                    elif self.sudoku.x == j and self.sudoku.y == i:
                        if self.sudoku.double_win:
                            color = colors['peach']
                        else:
                            color = colors['olive']
                    else:
                        if self.sudoku.double_win:
                            color = colors['lilac']
                        else:
                            color = colors['lime']
                    self.sudoku.cells[i][j]['square'].color = color

        self.canvas.draw()
        self.grid_batch.draw()
        self.fixed_cells_batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        i = (y - self.margin) // self.cell_width
        j = (x - self.margin) // self.cell_width
        if i in range(self.num ** 2) and j in range(self.num ** 2):
            if not self.sudoku.fixed_cells[i][j]:
                if self.sudoku.invalid_chars[i][j]:
                    active_color = colors['orange']
                else:
                    active_color = colors['lemon']
                self.sudoku.cells[i][j]['square'].color = active_color
                if self.sudoku.y != i or self.sudoku.x != j:
                    if self.sudoku.invalid_chars[self.sudoku.y][self.sudoku.x]:
                        passive_color = colors['scarlet']
                    else:
                        passive_color = colors['white']
                    self.sudoku.cells[self.sudoku.y][self.sudoku.x]['square'].color = passive_color
                self.sudoku.y = i
                self.sudoku.x = j

    def on_key_press(self, symbol, modifiers):
        if chr(symbol) in self.sudoku.symbols:
            self.sudoku.replace(chr(symbol))
        elif symbol in {key.DELETE, key.BACKSPACE, key.SPACE}:
            self.sudoku.replace(' ')
        elif symbol in {key.LCTRL, key.RCTRL, key.MOD_CTRL}:
            self.sudoku.solve()
        for i in range(self.num ** 2):
            for j in range(self.num ** 2):
                if self.sudoku.invalid_chars[i][j]:
                    if self.sudoku.fixed_cells[i][j]:
                        color = colors['ruby']
                    elif self.sudoku.x == j and self.sudoku.y == i:
                        color = colors['orange']
                    else:
                        color = colors['scarlet']
                else:
                    if self.sudoku.fixed_cells[i][j]:
                        color = colors['ash']
                    elif self.sudoku.x == j and self.sudoku.y == i:
                        color = colors['lemon']
                    else:
                        color = colors['white']
                self.sudoku.cells[i][j]['square'].color = color


def main(args):
    kwargs = {}
    if len(args) > 0:
        kwargs['num'] = int(args[0])
    if len(args) > 1:
        kwargs['fraction'] = float(args[1])
    if len(args) > 2:
        kwargs['grid_width'] = int(args[2])
    if len(args) > 3:
        kwargs['margin'] = int(args[3])
    Game(**kwargs)


if __name__ == '__main__':
    main(sys.argv[1:])
