"""
Classic Battleship Game, turn based, 5 ships
"""

import arcade
import PIL
import random
import pyglet.gl as gl
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Set how many rows and columns we will have on the board
ROW_COUNT = 10
COLUMN_COUNT = 10

# This sets the WIDTH and HEIGHT of each player_grid location
WIDTH = 50
HEIGHT = 50

# This sets the margin between each cell
# and on the edges of the screen.
MARGIN = 1

# Set the COMMANDS/options pane
OPTIONS = 350

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN + OPTIONS
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
TEXT_BOX_HEIGHT = 100

# Game states
START = -1				# Load in state
GAME = 0				# Action state where player attacks computer board
DIALOGUE = 1			# Unimplemented, but notifies when hit, miss, sunk, etc.
COMMANDS = 2			# Not fully implemented, but provides options for player to attack 
INSTRUCTIONS = 3		# Instructions state
GAME_OVER = 4			# Game over state with options to view final player/computer boards
USER = 5				# Initial User state to drop ships
COMPUTER = 6			# Computer state to attack user board
USER_FINAL = 7			# Final user state
COMPUTER_FINAL = 8		# Final computer state

# Set the sprite scaling factor
SPRITE_SCALING = 0.7

# Define the shapes of the single parts
ship_shapes = [
	[1, 1],

	[2, 2, 2],

	[3, 3, 3],

	[4 ,4 ,4 , 4],

	[5, 5, 5, 5, 5]
]

# Define the ship names
ships_lengths = {"Aircraft Carrier":5,
		 "Battleship":4,
		 "Submarine":3,
		 "Destroyer":3,
		 "PT Boat":2}

rem_health = {"Aircraft Carrier":5,
		 "Battleship":4,
		 "Submarine":3,
		 "Destroyer":3,
		 "PT Boat":2}


""" 
Colors for the sprites to take on
	blue: water
	white: miss
	gray: ship
	red: hit
"""
colors = [
		  (0,   0,   255),
		  (255, 255, 255),
		  (128, 128, 128),
		  (255, 0,   0  )
		  ]


def create_textures():
	""" 
	Create a list of images for sprites based on the global colors. 
	"""

	texture_list = []
	for color in colors:
		image = Image.new('RGB', (WIDTH, HEIGHT), color)
		texture_list.append(arcade.Texture(str(color), image=image))
	return texture_list


texture_list = create_textures()


def save_ships():
	"""
	Save a few sample ship images (basic)
	"""

	ship_desig = ['CV', 'BB', 'DD', 'SS', 'PT']
	ship_names = ['Aircraft Carrier', 'Battleship', 'Destroyer', 'Submarine', 'PT Boat']
	i = 0
	for ship in list(ships_lengths.keys()):
		ship_image = Image.new('RGB', (ships_lengths[ship] * WIDTH, HEIGHT), colors[2])
		draw = ImageDraw.Draw(ship_image)
		font = ImageFont.truetype("arial.ttf", 24)
		draw.text((0, 0), ship_names[i], (255,255,255), font=font)
		ship_image.save('Images/' + ship_desig[i] + '.png')
		i += 1

save_ships()

class TextButton:
	""" Text-based button """
	def __init__(self,
				 center_x, center_y,
				 width, height,
				 text,
				 font_size=18,
				 font_face="Arial",
				 face_color=arcade.color.LIGHT_GRAY,
				 highlight_color=arcade.color.WHITE,
				 shadow_color=arcade.color.GRAY,
				 button_height=2):
		self.center_x = center_x
		self.center_y = center_y
		self.width = width
		self.height = height
		self.text = text
		self.font_size = font_size
		self.font_face = font_face
		self.pressed = False
		self.face_color = face_color
		self.highlight_color = highlight_color
		self.shadow_color = shadow_color
		self.button_height = button_height

	def draw(self):
		""" Draw the button """
		arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width,
									 self.height, self.face_color)

		if not self.pressed:
			color = self.shadow_color
		else:
			color = self.highlight_color

		# Bottom horizontal
		arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
						 self.center_x + self.width / 2, self.center_y - self.height / 2,
						 color, self.button_height)

		# Right vertical
		arcade.draw_line(self.center_x + self.width / 2, self.center_y - self.height / 2,
						 self.center_x + self.width / 2, self.center_y + self.height / 2,
						 color, self.button_height)

		if not self.pressed:
			color = self.highlight_color
		else:
			color = self.shadow_color

		# Top horizontal
		arcade.draw_line(self.center_x - self.width / 2, self.center_y + self.height / 2,
						 self.center_x + self.width / 2, self.center_y + self.height / 2,
						 color, self.button_height)

		# Left vertical
		arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
						 self.center_x - self.width / 2, self.center_y + self.height / 2,
						 color, self.button_height)

		x = self.center_x
		y = self.center_y
		if not self.pressed:
			x -= self.button_height
			y += self.button_height

		arcade.draw_text(self.text, x, y,
						 arcade.color.BLACK, font_size=self.font_size,
						 width=self.width, align="center",
						 anchor_x="center", anchor_y="center")

	def on_press(self):
		self.pressed = True

	def on_release(self):
		self.pressed = False


def check_mouse_press_for_buttons(x, y, button_list):
	""" Given an x, y, see if we need to register any button clicks. """
	for button in button_list:
		if x > button.center_x + button.width / 2:
			continue
		if x < button.center_x - button.width / 2:
			continue
		if y > button.center_y + button.height / 2:
			continue
		if y < button.center_y - button.height / 2:
			continue
		button.on_press()


def check_mouse_release_for_buttons(x, y, button_list):
	""" If a mouse button has been released, see if we need to process
		any release events. """
	for button in button_list:
		if button.pressed:
			button.on_release()


class StartTextButton(TextButton):
	def __init__(self, center_x, center_y, width, text, action_function):
		super().__init__(center_x, center_y, width, 40, text, 18, "Arial")
		self.action_function = action_function

	def on_release(self):
		super().on_release()
		self.action_function()


class ShipClasses:
	"""
	Stores all the ships for the user to drop
	"""
	
	def __init__(self, screen_width = SCREEN_WIDTH - OPTIONS // 2, center_height = SCREEN_HEIGHT // 2, inv_height = OPTIONS):
		self.ship_sprites = arcade.SpriteList()
		self.screen_width = screen_width
		self.inv_height = inv_height
		self.center_height = center_height
		self.ship_list = ['Aircraft Carrier', 'Battleship', 'Destroyer', 'Submarine', 'PT Boat'] 

	def storeSprites(self):
		"""
		Stores each item in the player's inventory as a sprite in ship_sprites
		"""

		ship_locations = self.screen_width - 150
		location = 0
		for item in self.ship_list:
			if item == 'Aircraft Carrier':
				cv = arcade.Sprite('Images/CV.png', SPRITE_SCALING)
				cv.left = ship_locations
				cv.bottom = self.center_height + 80
				self.ship_sprites.append(cv)
			elif item == 'Battleship':
				bb = arcade.Sprite('Images/BB.png', SPRITE_SCALING)
				bb.left = ship_locations
				bb.bottom = self.center_height + 30
				self.ship_sprites.append(bb)
			elif item == 'Destroyer':
				dd = arcade.Sprite('Images/DD.png', SPRITE_SCALING)
				dd.left = ship_locations
				dd.bottom = self.center_height - 20
				self.ship_sprites.append(dd)
			elif item == 'Submarine':
				ss = arcade.Sprite('Images/SS.png', SPRITE_SCALING)
				ss.left = ship_locations
				ss.bottom = self.center_height - 70
				self.ship_sprites.append(ss)
			elif item == 'PT Boat':
				pt = arcade.Sprite('Images/PT.png', SPRITE_SCALING)
				pt.left = ship_locations
				pt.bottom = self.center_height - 120
				self.ship_sprites.append(pt)
	

	def use_ship(self, ship):
		"""
		Uses up an item and removes from inventory
		"""

		self.ship_list.remove(ship)
		self.ship_sprites = arcade.SpriteList()
		self.storeSprites()


	def showInventory(self):
		"""Draws the inventory and all its current components."""
		arcade.draw_rectangle_filled(self.screen_width, self.center_height, OPTIONS, SCREEN_HEIGHT, arcade.color.EGGPLANT)
		arcade.draw_text('INVENTORY:', self.screen_width - 100, self.center_height * 2 - 100, arcade.color.BLACK, 24)
		self.storeSprites()
		self.ship_sprites.draw()




class Battleship(arcade.Window):
	"""
	Main application class
	"""

	def __init__(self, width, height):
		"""
		Set up the application.
		"""
		
		super().__init__(width, height)

		# Create user/computer interfaces and game state
		self.state = START
		self.orientation = 0

		# Create ships and ship coordinates
		self.player_fleet = ShipClasses(SCREEN_WIDTH - OPTIONS // 2, SCREEN_HEIGHT // 2, OPTIONS)
		self.player_ship_coords = dict()
		self.computer_ship_coords = dict()

		# Create computer and player sprite boards and grids
		self.player_board = None
		self.computer_board = None
		self.player_grid = [[0 for x in range(COLUMN_COUNT)] for y in range(ROW_COUNT)]
		self.computer_grid = [[0 for x in range(COLUMN_COUNT)] for y in range(ROW_COUNT)]

		# Initialize player / computer health
		self.player_health = {'Aircraft Carrier':5,
		 'Battleship':4,
		 'Submarine':3,
		 'Destroyer':3,
		 'PT Boat':2}

		self.computer_health = {'Aircraft Carrier':5,
		 'Battleship':4,
		 'Submarine':3,
		 'Destroyer':3,
		 'PT Boat':2}

		arcade.set_background_color(arcade.color.BLACK)

		# Create button lists to take care of mouse commands and change game states
		self.button_list_start = []
		self.button_list_user = []
		self.button_list_howTo = []
		self.button_list_commands = []
		self.button_list_computer = []
		self.button_list_game_over = []
		self.button_list_user_final = []
		self.button_list_computer_final = []

		# Winner
		self.winner = -1

		# Create start game buttom which starts the game
		start_button = StartTextButton(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 150, 'Start', self.start_user)
		self.button_list_start.append(start_button)

		# Create the how to play button, which displays a tutorial screen
		how_to_play = StartTextButton(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, 150, 'How to Play', self.show_instructions)
		self.button_list_start.append(how_to_play)

		# Create Horizontal and Vertical Buttons for user when placing ships
		horizontal_button = StartTextButton(SCREEN_WIDTH - OPTIONS // 2 + 25, 80, 150, "Horizontal", self.set_horizontal)
		vertical_button = StartTextButton(SCREEN_WIDTH - OPTIONS // 2 + 25, 130, 150, "Vertical", self.set_vertical)
		self.button_list_user.append(horizontal_button)
		self.button_list_user.append(vertical_button)
		
		# Button to go back to the main menu
		back_to_menu = StartTextButton(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, 100, 'Return', self.show_start)
		self.button_list_howTo.append(back_to_menu)

		# Button to acknowledge computer move and revert to user interface
		back_to_game = StartTextButton(SCREEN_WIDTH - OPTIONS // 2 + 25, 80, 100, "OK", self.show_game)
		self.button_list_computer.append(back_to_game)


		# Display user board during user turn
		show_user_board = StartTextButton(SCREEN_WIDTH - OPTIONS // 2 - 25, 80, 200, "USER BOARD", self.show_computer)
		self.button_list_commands.append(show_user_board)
		
		# Game over button
		show_user_final = StartTextButton(SCREEN_WIDTH // 2, 50, 150, "User Final", self.show_player_board)
		show_computer_final = StartTextButton(SCREEN_WIDTH // 2, 110, 150, "Computer Final", self.show_computer_board)
		self.button_list_game_over.append(show_user_final)
		self.button_list_game_over.append(show_computer_final)

		# More game over buttons for accessing
		back_to_game_over = StartTextButton(SCREEN_WIDTH - OPTIONS // 2, 50, 300, "Back to Game Over", self.show_game_over)
		self.button_list_user_final.append(back_to_game_over)
		self.button_list_computer_final.append(back_to_game_over)


	def start_user(self):
		"""
		Start the game
		"""
		self.state = USER


	def show_instructions(self):
		"""
		start instruction screen
		"""
		self.state = INSTRUCTIONS


	def show_start(self):
		"""
		show start menu
		"""
		self.state = START


	def show_commands(self):
		"""
		Display the remaining ships that can be placed
		"""
		self.state = COMMANDS

	def show_game(self):
		"""
		Show the player board and revert to game state
		"""
		self.state = GAME
		#self.on_draw()

	def show_computer(self):
		"""
		Show the player's board and go to computer's state
		"""
		self.state = COMPUTER


	def show_game_over(self):
		"""
		Set the scene to game over
		"""
		self.state = GAME_OVER

	def set_horizontal(self):
		"""
		Set the ship horizontal
		"""
		self.orientation = 0

	def set_vertical(self):
		"""
		Set the ship vertical
		"""
		self.orientation = 1


	def place_horizontal(self, row, column, ship, player):
		"""
		Checks if placing a ship down horizontally is within the grid and doesn't collide
		"""

		if column + ship > 10:
			return False
		else:
			for i in range(ship):
				if player == USER and self.player_grid[row][column + i] == 2:
						return False
				elif self.computer_grid[row][column + i] == 2:
						return False
		
		for i in range(ship):
			j = row * COLUMN_COUNT + column
			if player == USER:
				self.player_grid[row][column + i] = 2
				self.player_board[j + i].set_texture(self.player_grid[row][column + i])
			else:
				self.computer_grid[row][column + i] = 2
				self.computer_board[j + i].set_texture(0) # Don't show computer ships
		
		return True



	def place_vertical(self, row, column, ship, player):
		"""
		Checks if placing a ship down vertically is within the grid and doesn't collide
		"""

		if row + ship > 10:
			return False
		else:
			for i in range(ship):
				if player == USER and self.player_grid[row + i][column] == 2:
						return False
				elif self.computer_grid[row + i][column] == 2:
						return False
		
		for i in range(ship):
			j = (row  + i) * COLUMN_COUNT + column
			if player == USER:
				self.player_grid[row + i][column] = 2
				self.player_board[j].set_texture(self.player_grid[row + i][column])
			else:
				self.computer_grid[row + i][column] = 2
				self.computer_board[j].set_texture(0) # Don't show computer ships

		return True



	def setup(self):
		"""
		Setup the board sprite lists for the player and the computer.
		"""

		self.player_board = arcade.SpriteList()
		self.computer_board = arcade.SpriteList()
		for row in range(ROW_COUNT):
			for column in range(COLUMN_COUNT):
				sprite = arcade.Sprite()
				sprite.textures = texture_list
				sprite.set_texture(self.player_grid[row][column])
				sprite.center_x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
				sprite.center_y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2
				self.player_board.append(sprite)

				sprite = arcade.Sprite()
				sprite.textures = texture_list
				sprite.set_texture(self.computer_grid[row][column])
				sprite.center_x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2	
			sprite.center_y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2
				self.computer_board.append(sprite)



	def show_player_board(self):
		"""
		Show the player board (final)
		"""

		# Set the state to user final
		self.state = USER_FINAL
		arcade.set_background_color(arcade.color.BLACK)
		for row in range(len(self.player_grid)):
			for column in range(len(self.player_grid[0])):
				v = self.player_grid[row][column]
				i = row * COLUMN_COUNT + column
				self.player_board[i].set_texture(v)

		arcade.start_render()
		self.player_board.draw()

		for button in self.button_list_user_final:
			button.draw()


	def show_computer_board(self):
		"""
		Show the computer board (final)
		"""

		# Set the state to computer final
		self.state = COMPUTER_FINAL
		arcade.set_background_color(arcade.color.BLACK)
		for row in range(len(self.computer_grid)):
			for column in range(len(self.computer_grid[0])):
				v = self.computer_grid[row][column]
				i = row * COLUMN_COUNT + column
				self.computer_board[i].set_texture(v)		

		arcade.start_render()
		self.computer_board.draw()
		
		for button in self.button_list_computer_final:
			button.draw()


	def on_mouse_press(self, x, y, button, modifiers):
		"""
		Called when the user presses a mouse button.
		"""

		# Change the x/y screen coordinates to player_grid coordinates
		column = x // (WIDTH + MARGIN)
		row = y // (HEIGHT + MARGIN)
		print(f"Click coordinates: ({x}, {y}). player_grid coordinates: ({row}, {column})")

		# If game state is START, then check of start buttons
		if self.state == START:
			check_mouse_press_for_buttons(x, y, self.button_list_start)

		# If the game state is USER, then the user is still placing ships on his/her board
		elif self.state == USER:
			valid = False
			
			# If user has no more ships to place, computer places ships
			if len(self.player_fleet.ship_list) == 0:
				self.state = GAME
				self.computer_place_ships()
				return

			# Check if the set orientation buttons were clicked
			check_mouse_press_for_buttons(x, y, self.button_list_user)

			if row < ROW_COUNT and column < COLUMN_COUNT:
				# Get the next ship and remove it from the directory
				ship_length = ships_lengths[self.player_fleet.ship_list[0]]
				#ships = ships[1:]
				
				if self.orientation == 0 and self.place_horizontal(row, column, ship_length, USER):
					#self.player_ship_coords[self.player_fleet.ship_list[0]] = []
					for i in range(ships_lengths[self.player_fleet.ship_list[0]]):
						self.player_ship_coords[(row, column + i)] = self.player_fleet.ship_list[0]
						print(self.player_fleet.ship_list[0])
					
					self.player_fleet.use_ship(self.player_fleet.ship_list[0])

				elif self.orientation == 1 and self.place_vertical(row, column, ship_length, USER):
					#self.player_ship_coords[self.player_fleet.ship_list[0]] = []
					for i in range(ships_lengths[self.player_fleet.ship_list[0]]):
						self.player_ship_coords[(row + i, column)] = self.player_fleet.ship_list[0]

					self.player_fleet.use_ship(self.player_fleet.ship_list[0])


		elif self.state == INSTRUCTIONS:
			check_mouse_press_for_buttons(x, y, self.button_list_howTo)

		elif self.state == COMPUTER:
			check_mouse_press_for_buttons(x, y, self.button_list_computer)


		# Make sure we are on-player_grid. It is possible to click in the upper right
		# corner in the margin and go to a player_grid location that doesn't exist

		elif self.state == GAME:
			check_mouse_press_for_buttons(x, y, self.button_list_commands)

			if row < ROW_COUNT and column < COLUMN_COUNT:
				i = row * COLUMN_COUNT + column

				#if self.user:

				# If hit water, then set to white (miss)
				if self.computer_grid[row][column] == 0 or self.computer_grid[row][column] == 2:
					self.computer_grid[row][column] += 1

					# Set the texture to display the effect
					self.computer_board[i].set_texture(self.computer_grid[row][column])
					self.on_draw()
					
					if self.computer_grid[row][column] == 3:
						self.computer_health[self.computer_ship_coords[(row, column)]] -= 1
						self.check_sink(row, column, USER)
						if self.check_win(USER):
							self.state = GAME_OVER
							return
					
					# Call computer's turn to attack player board
					self.computer_turn()

		elif self.state == GAME_OVER:
			check_mouse_press_for_buttons(x, y, self.button_list_game_over)
		elif self.state == USER_FINAL:
			check_mouse_press_for_buttons(x, y, self.button_list_user_final)
		elif self.state == COMPUTER_FINAL:
			check_mouse_press_for_buttons(x, y, self.button_list_computer_final)
					


	def on_mouse_release(self, x, y, button, key_modifiers):
		"""
		Called when a user releases a mouse button.
		"""

		if self.state == START:
			check_mouse_release_for_buttons(x, y, self.button_list_start)
		elif self.state == INSTRUCTIONS:
			check_mouse_release_for_buttons(x, y, self.button_list_howTo)
		elif self.state == USER:
			check_mouse_release_for_buttons(x, y, self.button_list_user)
		elif self.state == GAME:
			check_mouse_release_for_buttons(x, y, self.button_list_commands)
		elif self.state == COMPUTER:
			check_mouse_release_for_buttons(x, y, self.button_list_computer)
		elif self.state == GAME_OVER:
			check_mouse_release_for_buttons(x, y, self.button_list_game_over)
		elif self.state == USER_FINAL:
			check_mouse_release_for_buttons(x, y, self.button_list_user_final)
		elif self.state == COMPUTER_FINAL:
			check_mouse_release_for_buttons(x, y, self.button_list_computer_final)


	def computer_place_ships(self):
		"""
		Generate random but valid coordinates for the computer to place ships
		"""

		for ship in list(ships_lengths.keys()):
		
			#genreate random coordinates and validate the postion
			valid = False
			while not valid:

				x = random.randint(1,10)-1
				y = random.randint(1,10)-1
				o = random.randint(0,1)
				if o == 0 and self.place_horizontal(x, y, ships_lengths[ship], COMPUTER):
					valid = True
					for i in range(ships_lengths[ship]):
						self.computer_ship_coords[(x, y + i)] = ship
						print(ship)
				elif self.place_vertical(x, y, ships_lengths[ship], COMPUTER):
					valid = True
					for i in range(ships_lengths[ship]):
						self.computer_ship_coords[(x + i, y)] = ship
						print(ship)


	def computer_turn(self):
		"""
		Simple computer turn generator
		"""

		valid = False
		while not valid:			
			x = random.randint(1, 10) - 1
			y = random.randint(1, 10) - 1
			if self.player_grid[x][y] != 1 and self.player_grid[x][y] != 3:
				self.player_grid[x][y] += 1 # Note that increment turns water to miss, ship to hit
				i = x * COLUMN_COUNT + y
				self.player_board[i].set_texture(self.player_grid[x][y])
				valid = True

				if self.player_grid[x][y] == 3:
					#self.player_ship_coords[(x, y)]
					self.check_sink(x, y, COMPUTER)
					if self.check_win(COMPUTER):
						self.state = GAME_OVER
						return

		self.state = COMPUTER


	def check_sink(self, row, column, player):
		"""
		If a hit is registered, checks if a ship was sunk

		TODO: Implement dialogue screen to display ship statuses
		"""

		#print(self.player_ship_coords.keys())

		if player == USER and self.computer_health[self.computer_ship_coords[(row, column)]] == 0:
			print('SUNK')

			arcade.draw_text("You sank the enemy " + self.computer_ship_coords[(row, column)], SCREEN_WIDTH - OPTIONS // 2, SCREEN_HEIGHT // 2,
				arcade.color.WHITE, font_size=16,
				width=OPTIONS, align="center",
				anchor_x="center", anchor_y="center")

		elif player != USER and self.player_health[self.player_ship_coords[(row, column)]] == 0:
			arcade.draw_text("The enemey sank your " + self.player_ship_coords[(row, column)], SCREEN_WIDTH - OPTIONS // 2, SCREEN_HEIGHT // 2,
				arcade.color.WHITE, font_size=16,
				width=OPTIONS, align="center",
				anchor_x="center", anchor_y="center")



	def check_win(self, player):
		"""
		Check if either the player of the computer wins by sinking all the ships
		"""

		if player == USER:
			for ship in list(ships_lengths.keys()):
				if self.computer_health[ship] != 0:
					return False

			self.winner = USER
			return True
		else:
			for ship in list(ships_lengths.keys()):
				if self.player_health[ship] != 0:
					return False

			self.winner = COMPUTER
			return True


	def draw_start(self):
		"""
		Draw the start menu
		"""
		arcade.draw_texture_rectangle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.load_texture("Images/start.jpg"))

		for button in self.button_list_start:
			button.draw()
	


	def draw_instructions(self):
		"""
		Draw the instructions menu
		"""

		arcade.draw_texture_rectangle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.load_texture("Images/instructions.jpg"))

		arcade.draw_text("You are the commander of a fleet of ships.", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
				arcade.color.WHITE, font_size=16,
				width=SCREEN_WIDTH, align="center",
				anchor_x="center", anchor_y="center")

		arcade.draw_text("Your goal is to take out the hidden enemy fleet before they take you out.", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
				arcade.color.WHITE, font_size=16,
				width=SCREEN_WIDTH, align="center",
				anchor_x="center", anchor_y="center")

		arcade.draw_text("Place your ships in strategic positions, and hit hard, hit fast, hit often!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
				arcade.color.WHITE, font_size=16,
				width=SCREEN_WIDTH, align="center",
				anchor_x="center", anchor_y="center")


		for button in self.button_list_howTo:
			button.draw()


	def draw_user(self):
		"""
		Draw the user ship drop menu
		"""

		arcade.start_render()
		self.player_board.draw()
		self.player_fleet.showInventory()

		for button in self.button_list_user:
			button.draw()


	def draw_user_board(self):
		"""
		Display the player's board
		"""

		arcade.start_render()
		self.player_board.draw()
		for button in self.button_list_computer:
			button.draw()


	def draw_game(self):
		"""
		Draw the computer board for the player to attack
		"""
		
		arcade.start_render()
		self.computer_board.draw()

		# User command buttons, like go view user board
		for button in self.button_list_commands:
			button.draw()


	def draw_game_over(self):
		"""
		Draw the game over scene, for now blue for win, red for lose
		"""

		arcade.start_render()
		if self.winner == USER:
			arcade.set_background_color(arcade.color.BLUE)
		else:
			arcade.set_background_color(arcade.color.RED)

		for button in self.button_list_game_over:
			button.draw()



	#def draw_dialogue(self):


	def on_draw(self):
		""" 
		render the screen
		"""
		if self.state == START:
			self.draw_start()

		elif self.state == INSTRUCTIONS:
			self.draw_instructions()

		elif self.state == USER:
			self.draw_user()

		elif self.state == GAME:
			self.draw_game()

		elif self.state == COMPUTER:
			self.draw_user_board()

		elif self.state == GAME_OVER:
			self.draw_game_over()

		elif self.state == DIALOGUE:
			self.draw_dialogue()

		elif self.state == USER_FINAL:
			self.show_player_board()

		elif self.state == COMPUTER_FINAL:
			self.show_computer_board()



def main():
	""" 
	Create the game window, setup, run 
	"""

	my_game = Battleship(SCREEN_WIDTH, SCREEN_HEIGHT)
	my_game.setup()
	arcade.run()


if __name__ == "__main__":
	main()



