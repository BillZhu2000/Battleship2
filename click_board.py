# Basic click board that iterates through a few colors when clicked


import arcade
import os
import PIL
import random
import pyglet.gl as gl


# Set how many rows and columns we will have
ROW_COUNT = 20
COLUMN_COUNT = 15

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 30
HEIGHT = 30

# This sets the margin between each cell
# and on the edges of the screen.
MARGIN = 5

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN



colors = [
		  (0,   0,   0  ),
		  (255, 0,   0  ),
		  (0,   150, 0  ),
		  (0,   0,   255),
		  (255, 120, 0  ),
		  (255, 255, 0  ),
		  (180, 0,   255),
		  (0,   220, 220)
		  ]


def create_textures():
	""" 
	Create a list of images for sprites based on the global colors. 
	"""

	texture_list = []
	for color in colors:
		image = PIL.Image.new('RGB', (WIDTH, HEIGHT), color)
		image.save(str(color) + ".png")
		texture_list.append(arcade.Texture(str(color), image=image))
	return texture_list


texture_list = create_textures()


class MyGame(arcade.Window):
	"""
	Main application class.
	"""	

	def __init__(self, width, height):
		"""
		Set up the application.
		"""
		
		super().__init__(width, height)
		
		self.board_sprite_list = None

		# Create a 2 dimensional array. A two dimensional
		# array is simply a list of lists.
		self.grid = []
		for row in range(ROW_COUNT):
			# Add an empty array that will hold each cell
			# in this row
			self.grid.append([])
			for column in range(COLUMN_COUNT):
				self.grid[row].append(0)  # Append a cell

		arcade.set_background_color(arcade.color.BLACK)
		self.recreate_grid()


	def recreate_grid(self):
		"""
		Recreates the grid, slow method
		"""

		self.board_sprite_list = arcade.SpriteList(use_spatial_hash=False)
		for row in range(ROW_COUNT):
			for column in range(COLUMN_COUNT):
				sprite = arcade.Sprite()
				sprite.textures = texture_list
				sprite.set_texture(self.grid[row][column])
				sprite.center_x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
				sprite.center_y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2

				self.board_sprite_list.append(sprite)
				#sprite.draw()

		#self.board_sprite_list.draw()
		#self.board_sprite_list.update()
		#self.draw_grid(self.grid, 0, 0)
	

	def on_draw(self):
		"""
		Render the screen.
		"""

		# This command has to happen before we start drawing
		arcade.start_render()

		self.board_sprite_list.draw()

		# Manually draw the board
		#self.draw_grid(self.grid, 0, 0)
		gl.glFlush()

	

	def on_mouse_press(self, x, y, button, modifiers):
		"""
		Called when the user presses a mouse button.
		"""

		# Change the x/y screen coordinates to grid coordinates
		column = x // (WIDTH + MARGIN)
		row = y // (HEIGHT + MARGIN)

		print(f"Click coordinates: ({x}, {y}). Grid coordinates: ({row}, {column})")

		# Make sure we are on-grid. It is possible to click in the upper right
		# corner in the margin and go to a grid location that doesn't exist
		self.grid[row][column] = (self.grid[row][column] + 1) % len(colors)
		if row < ROW_COUNT and column < COLUMN_COUNT:

			v = self.grid[row][column]
			t = texture_list[v]
			i = row * COLUMN_COUNT + column
			#print(self.board_sprite_list[i]._texture)
			#self.board_sprite_list[i]._texture = t
			self.board_sprite_list[i].set_texture(v)



	"""
	def draw_rec(self, row, column, offset_x, offset_y):
		
		Update a single rectangle
		
		color = colors[self.grid[row][column]]
		x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
		y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2
		arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)


	
	def draw_grid(self, grid, offset_x, offset_y):
		
		Draw the grid. 
		
		for row in range(len(grid)):
			for column in range(len(grid[0])):
				# Figure out what color to draw the box
				if grid[row][column]:
					color = colors[grid[row][column]]
					# Do the math to figure out where the box is
					x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
					y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2

					# Draw the box
					arcade.draw_rectangle_filled(x, y, WIDTH, HEIGHT, color)
	"""

def main():
	MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
	arcade.run()

if __name__ == "__main__" :
	main()