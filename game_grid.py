import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing
import copy as cp
from tile import Tile


# A class for modeling the game grid
class GameGrid:
    # A constructor for creating the game grid based on the given arguments
    def __init__(self, grid_h, grid_w, game_speed):
        # set the dimensions of the game grid as the given arguments
        self.grid_height = grid_h
        self.grid_width = grid_w
        self.info_width = 5
        # create a tile matrix to store the tiles locked on the game grid
        self.tile_matrix = np.full((grid_h, grid_w), None)
        # create the tetromino that is currently being moved on the game grid
        self.current_tetromino = None

        self.next_tetromino = None
        # the game_over flag shows whether the game is over or not
        self.game_over = False
        # set the color used for the empty grid cells
        self.empty_cell_color = Color(192, 180, 166)
        # set the colors used for the grid lines and the grid boundaries
        self.line_color = Color(170, 155, 144)
        self.boundary_color = Color(170, 155, 144)
        # thickness values used for the grid lines and the grid boundaries
        self.line_thickness = 0.004
        self.box_thickness = 3 * self.line_thickness
        self.info_line_thickness = 3 * self.line_thickness

        # set initial score to zero
        self.score = 0

        # set game speed to argument
        self.game_speed = game_speed

        self.restart_flag = 0

    # A method for displaying the game grid
    def display(self):
        # clear the background to empty_cell_color
        stddraw.clear(self.empty_cell_color)
        # draw the game grid
        self.draw_grid()
        self.score = Tile.merge_tiles(self.tile_matrix, self.score)

        # draw the current/active tetromino if it is not None
        # (the case when the game grid is updated)
        if self.current_tetromino is not None:
            self.current_tetromino.draw()
        # draw a box around the game grid
        self.draw_info()
        self.draw_boundaries()
        # show the resulting drawing with a pause duration = 250 ms
        stddraw.show(self.game_speed)

    # A method for drawing the cells and the lines of the game grid
    def draw_grid(self):
        # for each cell of the game grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # if the current grid cell is occupied by a tile
                if self.tile_matrix[row][col] is not None:
                    # draw this tile
                    self.tile_matrix[row][col].draw(Point(col, row))

        # draw the inner lines of the game grid
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        # x and y ranges for the game grid
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method for drawing the boundaries around the game grid
    def draw_boundaries(self):
        # draw a bounding box around the game grid as a rectangle
        stddraw.setPenColor(self.boundary_color)  # using boundary_color
        # set the pen radius as box_thickness (half of this thickness is visible
        # for the bounding box as its lines lie on the boundaries of the canvas)
        stddraw.setPenRadius(self.box_thickness)
        # the coordinates of the bottom left corner of the game grid
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        # set pen radius for info box boundaries
        stddraw.setPenRadius(self.info_line_thickness)
        stddraw.rectangle(self.grid_width - 0.5, pos_y, self.info_width, self.grid_height)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method used checking whether the grid cell with the given row and column
    # indexes is occupied by a tile or not (i.e., empty)
    def is_occupied(self, row, col):
        # considering the newly entered tetrominoes to the game grid that may
        # have tiles with position.y >= grid_height
        if not self.is_inside(row, col):
            return False  # the cell is not occupied as it is outside the grid
        # the cell is occupied by a tile if it is not None
        return self.tile_matrix[row][col] is not None

    # A method for checking whether the cell with the given row and col indexes
    # is inside the game grid or not
    def is_inside(self, row, col):
        if row < 0 or row >= self.grid_height:
            return False
        if col < 0 or col >= self.grid_width:
            return False
        return True

    # A method for clearing full lines from the game grid
    def clear_lines(self):
        lines_to_clear = []

        # Check each row for full lines
        for row in range(self.grid_height):
            if all(self.tile_matrix[row]):
                lines_to_clear.append(row)
                # update score
                for tile in self.tile_matrix[row]:
                    self.score += tile.number

        # Clear full lines and shift down tiles
        for row in reversed(lines_to_clear):
            self.clear_line(row)
            self.shift_down_tiles(row)
        return lines_to_clear

    # A method for clearing a single line
    def clear_line(self, row):
        for col in range(self.grid_width):
            self.tile_matrix[row][col] = None

    # A method for shifting down tiles above the cleared line
    def shift_down_tiles(self, cleared_row):
        # Start from the cleared row and move upwards
        for row in range(cleared_row, self.grid_height - 1):
            # Shift each tile down one row
            for col in range(self.grid_width):
                self.tile_matrix[row][col] = self.tile_matrix[row + 1][col]

        # Set the top row to contain None values
        for col in range(self.grid_width):
            self.tile_matrix[self.grid_height - 1][col] = None

    # A method that locks the tiles of a landed tetromino on the grid checking
    # if the game is over due to having any tile above the topmost grid row.
    # (This method returns True when the game is over and False otherwise.)
    def update_grid(self, tiles_to_lock, blc_position):
        # necessary for the display method to stop displaying the tetromino
        self.current_tetromino = None
        # lock the tiles of the current tetromino (tiles_to_lock) on the grid
        n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
        for col in range(n_cols):
            for row in range(n_rows):
                # place each tile (occupied cell) onto the game grid
                if tiles_to_lock[row][col] is not None:
                    # compute the position of the tile on the game grid
                    pos = Point()
                    pos.x = blc_position.x + col
                    pos.y = blc_position.y + (n_rows - 1) - row
                    if self.is_inside(pos.y, pos.x):
                        self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
                    # the game is over if any placed tile is above the game grid
                    else:
                        self.game_over = True
        # return the value of the game_over flag
        return self.game_over

    # draw function for score, restart button and next tetromino
    def draw_info(self):

        # info grid settings
        stddraw.setPenColor(Color(167, 160, 151))
        stddraw.filledRectangle(self.grid_width - 0.5, -0.5, self.info_width, self.grid_height)
        info_center_x_scale = (self.grid_width + self.info_width / 2) - 0.5
        info_score_y_scale = (self.grid_height - 2)

        # draw the score
        stddraw.setPenColor(Color(255, 255, 255))
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(25)
        stddraw.boldText(info_center_x_scale, info_score_y_scale, "Score")
        stddraw.boldText(info_center_x_scale, info_score_y_scale - 0.75, str(self.score))

        # draw the next tetromino
        stddraw.boldText(info_center_x_scale, 7, "Next")
        if self.next_tetromino is not None:
            next_display = cp.deepcopy(self.next_tetromino)
            next_display.bottom_left_cell = Point()
            next_display.bottom_left_cell.x = self.grid_width + 1
            next_display.bottom_left_cell.y = 1.5
            next_display.draw()

        # Restart Game button
        stddraw.setPenColor(self.boundary_color)
        stddraw.filledRectangle(self.grid_width + 0.5, self.grid_height / 2 + 1, self.info_width - 2, 1)
        stddraw.setPenColor(Color(255, 255, 255))
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(20)
        stddraw.boldText(self.grid_width + 2, self.grid_height / 2 + 1.5, "Restart")

        if stddraw.mousePressed():
            # get the x and y coordinates of the locations of the mouse
            mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
            # check if these coordinates are inside the restart button
            if mouse_x >= self.grid_width + 0.5 and mouse_x <= self.grid_width + self.info_width - 1.5:
                if mouse_y >= self.grid_height / 2 + 1 and mouse_y <= self.grid_height / 2 + 2:
                    self.restart_flag = 1
