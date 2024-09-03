#!/usr/bin/env python3

import random
import time


class Sudoku:
    def __init__(self, num, total_symbols):
        self.num = num
        self.width = num ** 2
        self.symbols = total_symbols[:num ** 2]
        self.grid = []
        self.cells = [[{} for _ in range(num ** 2)] for _ in range(num ** 2)]
        self.grid_valid = True
        self.fixed_cells = []
        self.original_grid = []
        self.invalid_chars = []
        self.initialize_invalid_chars()
        self.x, self.y = 0, 0
        self.win = False
        self.double_win = False

    def ordered_grid(self):
        strands = [self.symbols[start * self.num:(start + 1) * self.num] for start in range(self.num)]

        grid = [[0] * self.num ** 2 for _ in range(self.num ** 2)]
        for i in range(self.num ** 2):
            for j in range(self.num ** 2):
                strand_num = (i % self.num + j // self.num) % self.num
                grid[i][j] = strands[strand_num][(i // self.num + j % self.num) % self.num]
        self.grid = grid

    def randomize_grid(self, swap_num=None):
        swap_num = self.num ** 3 if swap_num is None else None
        symbols_copy = self.symbols.copy()
        random.shuffle(symbols_copy)
        strands = [symbols_copy[start * self.num:(start + 1) * self.num] for start in range(self.num)]

        grid = [[0] * self.num ** 2 for _ in range(self.num ** 2)]
        for i in range(self.num ** 2):
            for j in range(self.num ** 2):
                strand_num = (i % self.num + j // self.num) % self.num
                grid[i][j] = strands[strand_num][(i // self.num + j % self.num) % self.num]

        for _ in range(swap_num):
            is_row = random.choice([True, False])
            a, b = random.sample(list(range(self.num)), 2)
            box_start = random.choice(list(range(self.num))) * self.num
            if is_row:
                grid[box_start + a], grid[box_start + b] = grid[box_start + b], grid[box_start + a]
            else:
                for i in range(len(grid)):
                    grid[i][box_start + a], grid[i][box_start + b] = grid[i][box_start + b], grid[i][box_start + a]

        self.grid = grid

    def get_symbols_in_box(self, x, y):
        symbols = set()
        for i in range(y % self.num, (y + 1) % self.num):
            for j in range(x % self.num, (x + 1) % self.num):
                symbols.add(self.grid[i][j])
        return symbols & set(self.symbols)

    def get_symbols_in_row(self, y):
        return set(self.grid[y]) & set(self.symbols)

    def get_symbols_in_column(self, x):
        return {row[x] for row in self.grid} & set(self.symbols)

    def get_candidates(self, x, y):
        return sorted(
            list(
                set(self.symbols) - (
                    self.get_symbols_in_box(x, y)
                    | self.get_symbols_in_row(y)
                    | self.get_symbols_in_column(x)
                )
            )
        )

    def find_free_cells(self):
        free_cell_coords = []
        for i in range(self.num ** 2):
            for j in range(self.num ** 2):
                if not self.fixed_cells[i][j]:
                    free_cell_coords.append((j, i))
        return free_cell_coords

    def solve(self):
        free_cell_coords = self.find_free_cells()
        print(free_cell_coords)
        index = 0
        candidates_last_tested = [0] * len(free_cell_coords)
        solved = False
        while True:
            if index == len(free_cell_coords):
                solved = True
                break
            self.x, self.y = free_cell_coords[index]
            print(self.x, self.y)
            last_tested_candidate = candidates_last_tested[index]
            if last_tested_candidate == 0:
                candidate_index = 0
            else:
                candidate_index = self.symbols.index(last_tested_candidate) + 1
            while candidate_index < len(self.symbols):
                candidate = self.symbols[candidate_index]
                candidates_last_tested[index] = candidate
                self.replace(candidate, with_check=False)
                # self.grid[y][x] = candidate
                row_valid = self.check_row_validity(self.y)
                if not row_valid:
                    candidate_index += 1
                    self.replace(' ', with_check=False)
                    continue
                column_valid = self.check_column_validity(self.x)
                if not column_valid:
                    candidate_index += 1
                    self.replace(' ', with_check=False)
                    continue
                box_valid = self.check_box_validity(self.x, self.y)
                if not box_valid:
                    candidate_index += 1
                    self.replace(' ', with_check=False)
                    continue

                print(self.x, self.y, candidate)
                break
            if self.grid[self.y][self.x] == ' ':
                candidates_last_tested[index] = 0
                index -= 1
            else:
                index += 1
        self.check_for_win()
        #
        #
        #
        #
        #
        #
        # for i in range(self.num ** 2):
        #     for j in range(self.num ** 2):
        #         if self.grid[i][j] == ' ':
        #             candidates = self.get_candidates(j, i)
        #             for candidate in candidates:
        #                 self.grid[i][j] = candidate
        #                 self.cells[i][j]['label'].text = candidate
        #                 print(i, j, candidate)
        #                 game.on_draw()
        #                 if self.solve(game):
        #                     return True
        #                 else:
        #                     self.grid[i][j] = ' '
        #                     self.cells[i][j]['label'].text = ' '
        #                     game.on_draw()
        #                     continue
        # if self.grid_is_full():
        #     self.win = True
        #     return True
        # else:
        #     self.win = False
        #     return False

    def replace(self, char, with_check=True):
        if not self.fixed_cells[self.y][self.x]:
            self.grid[self.y][self.x] = char
            self.cells[self.y][self.x]['label'].text = char
            if with_check:
                self.check_grid_validity()
                self.check_for_win()

    def randomize_fixed_cells(self, fraction=0.5):
        coords = []
        for i in range(self.num ** 2):
            for j in range(self.num ** 2):
                coords.append((j, i))
        fixed_coords = random.sample(coords, k=int(self.num ** 4 * fraction))
        for i in range(self.num ** 2):
            row = []
            for j in range(self.num ** 2):
                row.append((j, i) in fixed_coords)
            self.fixed_cells.append(row)
        self.original_grid = [[char for char in row] for row in self.grid]
        self.clear_non_fixed_cells()

    def check_row_validity(self, y):
        used_symbols = set()
        for j in self.grid[y]:
            if j in self.symbols:
                if j in used_symbols:
                    return False
                used_symbols.add(j)
        return True

    def check_column_validity(self, x):
        used_symbols = set()
        for row in self.grid:
            if row[x] in self.symbols:
                if row[x] in used_symbols:
                    return False
                used_symbols.add(row[x])
        return True

    def check_box_validity(self, x, y):
        used_symbols = set()
        for i, row in enumerate(self.grid):
            for j, char in enumerate(row):
                if i // self.num == y // self.num and j // self.num == x // self.num:
                    if char in self.symbols:
                        if char in used_symbols:
                            return False
                        used_symbols.add(char)
        return True

    def get_invalid_coords_for_cell(self, x, y):
        coords = self.find_matching_in_row(x, y)
        coords |= self.find_matching_in_column(x, y)
        coords |= self.find_matching_in_box(x, y)
        if len(coords) > 0:
            coords.add((x, y))
        return coords

    def check_grid_validity(self):
        coords = set()
        for y in range(self.num ** 2):
            for x in range(self.num ** 2):
                coords |= self.get_invalid_coords_for_cell(x, y)
        self.initialize_invalid_chars()
        for x, y in coords:
            self.invalid_chars[y][x] = True
        self.grid_valid = len(coords) == 0

    def find_matching_in_row(self, x, y):
        char = self.grid[y][x]
        coords = set()
        for j, other in enumerate(self.grid[y]):
            if j == x:
                continue
            if other == char and char != ' ':
                coords.add((j, y))
        return coords

    def find_matching_in_column(self, x, y):
        char = self.grid[y][x]
        coords = set()
        for i, row in enumerate(self.grid):
            if i == y:
                continue
            if row[x] == char and char != ' ':
                coords.add((x, i))
        return coords

    def find_matching_in_box(self, x, y):
        char = self.grid[y][x]
        coords = set()
        for i, row in enumerate(self.grid):
            for j, other in enumerate(row):
                if i // self.num == y // self.num and j // self.num == x // self.num:
                    if i == y and j == x:
                        continue
                    if other == char and char != ' ':
                        coords.add((j, i))
        return coords

    def initialize_invalid_chars(self):
        self.invalid_chars = []
        for i in range(self.num ** 2):
            row = []
            for j in range(self.num ** 2):
                row.append(False)
            self.invalid_chars.append(row)

    def clear_non_fixed_cells(self):
        for i in range(self.num ** 2):
            for j in range(self.num ** 2):
                if not self.fixed_cells[i][j]:
                    self.grid[i][j] = ' '

    def grid_is_full(self):
        symbol_sum = sum(sum(1 for char in row if char in self.symbols) for row in self.grid)
        return symbol_sum == self.num ** 4

    def check_for_win(self):
        if self.grid_is_full() and self.grid_valid:
            self.win = True
            if self.grid == self.original_grid:
                self.double_win = True
        else:
            self.win, self.double_win = False, False
