"""
Classic Battleship Game
"""

import arcade
import PIL
import random
import pyglet.gl as gl
import os
import numpy as np

# Set how many rows and columns we will have
ROW_COUNT = 100
COLUMN_COUNT = 100

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 10
HEIGHT = 10

# This sets the margin between each cell
# and on the edges of the screen.
MARGIN = 1

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN


def create_textures():
	""" 
	Create a list of images for sprites based on the global colors. 
	"""

	texture_list = []
	for color in colors:
		image = PIL.Image.new('RGB', (WIDTH, HEIGHT), color)
		texture_list.append(arcade.Texture(str(color), image=image))
	return texture_list


texture_list = create_textures()


class Battleship(arcade.Window):
	"""
	Main application class
	"""

	def __init__(self, width, height):
		"""
		Set up the application.
		"""
		
		super().__init__(width, height)
		self.board_sprite_list = None

		# Make a grid
		self.grid = np.zeros((ROW_COUNT, COLUMN_COUNT))

		arcade.set_background_color(arcade.color.BLUE)


	def setup(self):
		self.board_sprite_list = arcade.SpriteList()
		for row in ROW_COUNT:
			for column in COLUMN_COUNT:
				sprite = arcade.Sprite()
				sprite.textures = texture_list
				sprite.set_texture(self.board[row][column])
				sprite.center_x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
				sprite.center_y = SCREEN_HEIGHT - (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2

				self.board_sprite_list.append(sprite)






