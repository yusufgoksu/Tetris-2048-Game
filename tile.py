import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles
import random


# A class for modeling numbered tiles as in 2048
class Tile:
    # Class variables shared among all Tile objects
    # ---------------------------------------------------------------------------
    # the value of the boundary thickness (for the boxes around the tiles)
    boundary_thickness = 0.004
    # font family and font size used for displaying the tile number
    font_family, font_size = "Arial", 14

    # colors for numbers
    COLORS = {
        2: {
            "background_color": Color(238, 228, 218),
            "foreground_color": Color(138, 129, 120)
        },
        4: {
            "background_color": Color(236, 224, 200),
            "foreground_color": Color(138, 129, 120)
        },
        8: {
            "background_color": Color(243, 177, 121),
            "foreground_color": Color(255, 255, 255)
        },
        16: {
            "background_color": Color(245, 150, 98),
            "foreground_color": Color(255, 255, 255)
        },
        32: {
            "background_color": Color(249, 123, 97),
            "foreground_color": Color(255, 255, 255)
        },
        64: {
            "background_color": Color(245, 100, 60),
            "foreground_color": Color(255, 255, 255)
        },
        128: {
            "background_color": Color(238, 228, 218),
            "foreground_color": Color(255, 255, 255)
        },
        256: {
            "background_color": Color(237, 203, 99),
            "foreground_color": Color(255, 255, 255)
        },
        512: {
            "background_color": Color(238, 201, 84),
            "foreground_color": Color(255, 255, 255)
        },
        1024: {
            "background_color": Color(239, 196, 64),
            "foreground_color": Color(255, 255, 255)
        },
        2048: {
            "background_color": Color(238, 194, 45),
            "foreground_color": Color(255, 255, 255)
        }
    }

    # A constructor that creates a tile with 2 as the number on it
    def __init__(self):
        # set the number on this tile
        random_numbers = [2, 4]
        # set the number on the tile
        self.number = random_numbers[random.randint(0, len(random_numbers) - 1)]
        # set the colors of this tile
        self.set_color()
        self.box_color = Color(170, 155, 144)  # box (boundary) color

    def set_color(self):
        self.background_color = self.COLORS[self.number]['background_color']
        self.foreground_color = self.COLORS[self.number]['foreground_color']

    # A method for drawing this tile at a given position with a given length
    def draw(self, position, length=1):  # length defaults to 1
        # draw the tile as a filled square
        stddraw.setPenColor(self.background_color)
        stddraw.filledSquare(position.x, position.y, length / 2)
        # draw the bounding box around the tile as a square
        stddraw.setPenColor(self.box_color)
        stddraw.setPenRadius(Tile.boundary_thickness)
        stddraw.square(position.x, position.y, length / 2)
        stddraw.setPenRadius()  # reset the pen radius to its default value
        # draw the number on the tile
        stddraw.setPenColor(self.foreground_color)
        stddraw.setFontFamily(Tile.font_family)
        stddraw.setFontSize(Tile.font_size)
        stddraw.text(position.x, position.y, str(self.number))

    def if_matches(self, tile):
        # if the number on the tile is equal to the number on the current tile
        if self.number == tile.number and self.number < 2048:
            # set the number on the current tile to the sum of the two numbers
            self.number = self.number * 2
            # increase the score by the value of the number on the current tile
            # Remove the tile and update the color of the current tile
            tile.number = None

            # Update the color of the current tile
            self.set_color()
            # return True to indicate that the tiles were matched
            return self.number
        # return False to indicate that the tiles were not matched
        else:
            return 0

    # Merges tiles in the tile matrix.
    def merge_tiles(tile_matrix, score):
        # iterate through the tile matrix
        for col in range(len(tile_matrix[0])):
            for row in range(len(tile_matrix)):
                try:
                    # if the tile to the top of the current tile is not empty
                    # and the number on the current tile is equal to the number
                    # on the tile to the top merge them
                    if tile_matrix[row][col] != None and tile_matrix[row + 1][col] != None and tile_matrix[row][
                        col].number == tile_matrix[row + 1][col].number:
                        score += tile_matrix[row][col].if_matches(tile_matrix[row + 1][col])
                        tile_matrix[row + 1][col] = None
                        # After merging the tiles, move the tiles down
                        for row_index in range(row + 1, len(tile_matrix)):
                            if tile_matrix[row_index][col] != None:
                                tile_matrix[row_index - 1][col] = tile_matrix[row_index][col]
                                tile_matrix[row_index][col] = None
                except IndexError:
                    pass
                # check neighboring tiles
                right_neighbour = tile_matrix[row + 1][col] == None if row + 1 < len(tile_matrix) else True
                up_neighbour = tile_matrix[row][col + 1] == None if col + 1 < len(tile_matrix[0]) else True
                left_neighbour = tile_matrix[row - 1][col] == None if row - 1 >= 0 else True
                down_neighbour = tile_matrix[row][col - 1] == None if col - 1 >= 0 else True
                # if the current tile is not empty and the neighbors are empty
                # move the current tile to the any empty neighbor
                # do not do in the first row
                if row != 0:
                    if tile_matrix[row][
                        col] != None and right_neighbour and left_neighbour and up_neighbour and down_neighbour:
                        tile_matrix[row - 1][col] = tile_matrix[row][col]
                        tile_matrix[row][col] = None
                        row -= 1
                row += 1
        return score
