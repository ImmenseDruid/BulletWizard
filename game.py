import pygame, entities, ui
import math, random
import numpy as np
import os
from pygame.locals import *


pygame.init()

font = pygame.font.SysFont('Courier New', 30)

COL_DEBUG = (255, 0, 255)
scale = 1
width = 1280
height = 720
camera = entities.Camera((width, height))
screen = pygame.display.set_mode((int(width * scale), int(height * scale)))
window = pygame.Surface((width, height))


def draw_text(text, font, color, pos, centered = False):
	img = font.render(text, True, color)
	if centered:
		window.blit(img, (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2))
	else:
		window.blit(img, pos)

img_wall = pygame.image.load(os.path.join(os.path.join('Images', 'Walls'), 'wall.png')).convert()
img_floor = pygame.image.load(os.path.join(os.path.join('Images', 'Floors'), 'floor.png')).convert()
img_bullets = []
for file in os.listdir(os.path.join(os.path.join('Images', 'Staff'), 'Orbs')):
	if os.path.isfile(os.path.join(os.path.join('Images', 'Staff'), file)):
		surf = pygame.image.load(os.path.join(os.path.join(os.path.join('Images', 'Staff'), 'Orbs'), file)).convert_alpha()
		surf.set_colorkey((0,0,0))

		img_bullets.append(surf)
img_player = pygame.image.load(os.path.join(os.path.join('Images', 'Entities'), 'player.png')).convert_alpha()
img_cultist = pygame.image.load(os.path.join(os.path.join('Images', 'Entities'), 'cultist.png')).convert_alpha()
img_weapons = []
for file in os.listdir(os.path.join('Images', 'Staff')):
	if os.path.isfile(os.path.join(os.path.join('Images', 'Staff'), file)):
		surf = pygame.image.load(os.path.join(os.path.join('Images', 'Staff'), file)).convert_alpha()
		surf.set_colorkey((0,0,0))

		img_weapons.append(surf)


img_enterance = pygame.image.load(os.path.join('Images', 'DungeonEnterance.png')).convert_alpha()
img_exit = pygame.image.load(os.path.join('Images', 'DungeonExit.png')).convert_alpha()
img_play_button = pygame.image.load(os.path.join(os.path.join('Images', 'UI'), 'play_button.png')).convert_alpha()
img_chest_open = pygame.image.load(os.path.join('Images', 'Chest_open.png')).convert_alpha()
img_chest_closed = pygame.image.load(os.path.join('Images', 'Chest_closed.png')).convert_alpha()
img_health_pickup = pygame.image.load(os.path.join('Images', 'Health_Pickup.png')).convert_alpha()

tile_index = {1 : img_wall}

def get_mouse_pos():
	return (pygame.mouse.get_pos()[0] // scale + camera.pos[0], pygame.mouse.get_pos()[1] // scale + camera.pos[1])

CHUNK_SIZE = 32

floor_map = []

for i in range(width // 32 + 4):
	floor_map.append([])
	for j in range(height // 32 + 4):
		floor_map[i].append([i * 32, j * 32])

#TODO : 
#  : WEDNESDAY : FIX DUPLICATION BUG, CREATE MORE ENEMIES / BETTER ENEMY AI (STEERING BEHAVIORS, WITH WEIGHTED CHOICE), CREATE BOSS, CREATE MORE WEAPONS, CREATE SHIELD BURST (PUSH PROJECTILES AWAY), CHANGE DROP TO Q, CREATE SPECIAL POWERS??? (TURN SHIELD BURST INTO OTHER THINGS MAYBE OR JUST MORE POWERS THAT YOU CAN BUY AND STUFF)
#  : THURSDAY : CREATE BETTER MAP GENERATION, CREATE ROOM CREATOR, MAPS WILL GENERATE HANDMADE ROOMS ALONG A PATH, EVENTUALLY LEADING TO ITEM ROOMS, A SHOP, AND A BOSS
#  : FRIDAY : POLISH POLISH POLISH (Polish also means UI)
#  : SATURDAY : MUSIC, SFX, IF NOT ENOUGH TIME JUST USE SOME OF THE PREMADE ASSESTS WE HAVE 

def generate_chunks(x, y):

	chunk = []
	for y_pos in range(CHUNK_SIZE):
		target_y = y * CHUNK_SIZE + y_pos
		noise = np.random.normal(0, 1, CHUNK_SIZE)
		tiles = []
		for x_pos in range(CHUNK_SIZE):
			target_x = x * CHUNK_SIZE + x_pos

			tile_type = 0
			if noise[x_pos] < 0.75:
				tile_type = 0
			elif noise[x_pos] > 0.75:
				tile_type = 1

			tiles.append([[target_x, target_y], tile_type])
		chunk.append(tiles)
	if False:
		for k in range(3):

			for j in range(len(chunk)):
				for i in range(len(chunk[j])):
					if j > 0 and i > 0:
						walls = 0 
						for offset_j in range(-1, 1):
							for offset_i in range(-1, 1):
								walls += chunk[j + offset_j][i + offset_i][1]

						if walls >= 4:
							chunk[j][i][1] = 1
						else:
							chunk[j][i][1] = 0
					else:
						if (j == 0 or j == len(chunk) - 1) and (i >= len(chunk[j]) // 2 - 1 and i <= len(chunk[j]) // 2 + 1):
							chunk[j][i][1] = 0
						else:
							chunk[j][i][1] = 1
						if i == 0 and (j >= len(chunk) // 2 - 1 and j <= len(chunk) // 2 + 1):
							chunk[j][i][1] = 0
						else:
							chunk[j][i][1] = 1
				


	chunck_data = []
	for j in range(len(chunk)):
		for i in range(len(chunk[j])):
			if chunk[j][i][1] != 0:	
				chunck_data.append(chunk[j][i])

	#print(chunck_data)

	return chunck_data


START = 0
END = 1
ESSENTIAL = 2
EMPTY = 3
WALL = 4
OUTERWALL = 5
CHEST = 6
ENTERANCE = 7
EXIT = 8
ENEMY = 9

RANDOM = 99

class PathTile():
	def  __init__(self, tile_type, start_pos, min_bounds, max_bounds, current_tiles):
		self.tile_type = tile_type
		self.position = start_pos
		self.adjacent_path_tiles = self.get_adjacent_path_tiles(min_bounds, max_bounds, self.position, current_tiles)

	def get_adjacent_path_tiles(self, min_bounds, max_bounds, start_pos, current_tiles):
		path_tiles = []
		if start_pos[1] + 1 < max_bounds and f'{start_pos[0]};{start_pos[1] + 1}' not in current_tiles:
			path_tiles.append([start_pos[0], start_pos[1] + 1])
		if start_pos[0] + 1 < max_bounds and f'{start_pos[0] + 1};{start_pos[1]}' not in current_tiles:
			path_tiles.append([start_pos[0] + 1, start_pos[1]])
		if start_pos[1] - 1 > min_bounds and f'{start_pos[0]};{start_pos[1] - 1}' not in current_tiles:
			path_tiles.append([start_pos[0], start_pos[1] - 1])
		if start_pos[0] - 1 > min_bounds and f'{start_pos[0] - 1};{start_pos[1]}' not in current_tiles and self.tile_type != ESSENTIAL:
			path_tiles.append([start_pos[0] - 1, start_pos[1]])

		return path_tiles

	
class DungeonManager():
	def __init__(self):
		self.grid_positions = {}
		self.min_bounds = 0
		self.max_bounds = None
		self.start_pos = None
		self.end_pos = None

	def start_dungeon(self):
		self.grid_positions.clear()
		self.max_bounds = random.randrange(50, 101)

		self.BuildEssentialPath()

		self.BuildRandomPath()

		print(self.grid_positions)



	def BuildEssentialPath(self):
		startY = random.randrange(0, self.max_bounds + 1)
		ePath = PathTile(ESSENTIAL, (0, startY), self.min_bounds, self.max_bounds, self.grid_positions)
		self.start_pos = ePath.position
		bound_tracker = 0 

		while bound_tracker < self.max_bounds:
			self.grid_positions[f'{ePath.position[0]};{ePath.position[1]}'] = [[ePath.position[0], ePath.position[1]], EMPTY]
			adj_tile_count = len(ePath.adjacent_path_tiles)
			nextPos = None
			if adj_tile_count > 0:
				randomIndex = random.randrange(0, adj_tile_count)
				nextPos = ePath.adjacent_path_tiles[randomIndex]
			else:
				break 

			nextEPath = PathTile(ESSENTIAL, nextPos, self.min_bounds, self.max_bounds, self.grid_positions)
			if nextEPath.position[0] > ePath.position[0] or (nextEPath.position[0] == self.max_bounds - 1 and random.randrange(0,2) == 1):
				bound_tracker += 1 
			ePath = nextEPath

		if f'{ePath.position[0]};{ePath.position[1]}' not in self.grid_positions:
			self.grid_positions[f'{ePath.position[0]};{ePath.position[1]}'] = [[ePath.position[0], ePath.position[1]], EMPTY]

		self.end_pos = ePath.position

	def BuildRandomPath(self):
		pathQueue = []
		for tile in self.grid_positions:
			pathQueue.append(PathTile(RANDOM, self.grid_positions[tile][0], self.min_bounds, self.max_bounds, self.grid_positions))

		for tile in pathQueue:
			adj_tile_count = len(tile.adjacent_path_tiles)

			if adj_tile_count != 0:
				if random.randrange(0, 5) == 1:
					self.BuildRandomChamber(tile)
				elif random.randrange(0, 5) == 1 or (tile.tile_type == RANDOM and adj_tile_count > 1):
					randomIndex = random.randrange(0, adj_tile_count)

					newPos = tile.adjacent_path_tiles[randomIndex]

					if f'{newPos[0]};{newPos[1]}' not in self.grid_positions:
						if random.randrange(0, 20) == 1:
							self.grid_positions[f'{newPos[0]};{newPos[1]}'] = [[newPos[0], newPos[1]], ENEMY]
						else:
							self.grid_positions[f'{newPos[0]};{newPos[1]}'] = [[newPos[0], newPos[1]], EMPTY]

						newRPath = PathTile(RANDOM, newPos, self.min_bounds, self.max_bounds, self.grid_positions)
						pathQueue.append(newRPath)

	def BuildRandomChamber(self, tile):
		chamberSize = random.randrange(3, 6)
		adj_tile_count = len(tile.adjacent_path_tiles)
		randomIndex = random.randrange(0, adj_tile_count)
		chamberOrigin = tile.adjacent_path_tiles[randomIndex]

		for x in range(chamberOrigin[0], chamberOrigin[0] + chamberSize):
			for y in range(chamberOrigin[1], chamberOrigin[1] + chamberSize):
				chamberTilePos = (x, y)
				if f'{chamberTilePos[0]};{chamberTilePos[1]}' not in self.grid_positions and chamberTilePos[0] < self.max_bounds and chamberTilePos[0] > 0 and	chamberTilePos[1] < self.max_bounds and chamberTilePos[1] > 0:
					if random.randrange(0, 100) == 1:
						self.grid_positions[f'{chamberTilePos[0]};{chamberTilePos[1]}'] = [[chamberTilePos[0], chamberTilePos[1]], CHEST]
					elif random.randrange(0, 30) == 1:
						self.grid_positions[f'{chamberTilePos[0]};{chamberTilePos[1]}'] = [[chamberTilePos[0], chamberTilePos[1]], ENEMY]
					else:
						self.grid_positions[f'{chamberTilePos[0]};{chamberTilePos[1]}'] = [[chamberTilePos[0], chamberTilePos[1]], EMPTY]

class BoardManager():
	def __init__(self):
		self.collumns = 10
		self.rows = 10
		self.exit = None
		self.outerWallTiles = []
		self.floorTiles = []
		self.wallTiles = []
		self.draw_world = True
		self.grid_positions = {}
		self.dungeon_grid_positions = {}


	def setup(self):
		for x in range(self.collumns):
			for y in range(self.rows):
				self.grid_positions[f'{x};{y}'] = [[x, y], EMPTY]
				#draw tile

	def addToBoard(self, playerx, playery):
		for x in range(playerx - 10, playerx + 10 + 1):
			for y in range(playery - 10, playery + 10 + 1):
				self.addTiles((x, y))

	def addTiles(self, tilePos):
		if f'{tilePos[0]};{tilePos[1]}' not in self.grid_positions:
			self.grid_positions[f'{tilePos[0]};{tilePos[1]}'] = [[tilePos[0], tilePos[1]], EMPTY]

			if random.randrange(0,4) == 1:
				self.grid_positions[f'{tilePos[0]};{tilePos[1]}'] = [[tilePos[0], tilePos[1]], WALL]

			elif random.randrange(0, 200) == 1:
				self.grid_positions[f'{tilePos[0]};{tilePos[1]}'] = [[tilePos[0], tilePos[1]], ENTERANCE]
			elif random.randrange(0, 40) == 1:
				self.grid_positions[f'{tilePos[0]};{tilePos[1]}'] = [[tilePos[0], tilePos[1]], ENEMY]


	def setDungeonBoard(self, dungeon_tiles, bound, end_pos):
		
		for tile in dungeon_tiles:
			for x in range(dungeon_tiles[tile][0][0] - 1, dungeon_tiles[tile][0][0] + 2):
				for y in range(dungeon_tiles[tile][0][1] - 1, dungeon_tiles[tile][0][1] + 2):
					if f'{x};{y}' not in dungeon_tiles:
						self.dungeon_grid_positions[f'{x};{y}'] = [[x, y], OUTERWALL]


		for tile in dungeon_tiles:
			self.dungeon_grid_positions[tile] = dungeon_tiles[tile]

		self.dungeon_grid_positions[f'{end_pos[0]};{end_pos[1]}'] = [[end_pos[0], end_pos[1]], EXIT]
		self.draw_world = False
	
	def setWorldBoard(self):
		self.dungeon_grid_positions.clear()
		self.draw_world = True

class GameManager():
	def __init__(self):
		self.bm = BoardManager()
		self.bm.setup()
		self.dm = DungeonManager()



	def enterDungeon(self):
		self.dm.start_dungeon()
		self.bm.setDungeonBoard(self.dm.grid_positions, self.dm.max_bounds, self.dm.end_pos)

	def exitDungeon(self):
		self.bm.setWorldBoard()



def main():

	gm = GameManager()
	#gm.bm.setup()

	

	player = entities.Player([200, 200], img_player)
	wp = entities.Weapon(1, 400, player, 1, 150, img_bullets[0], img_weapons[0])
	player.weapon = wp



	#500 -> 300
	#250 -> 150

	game_map = {}
	temp_tiles = {}
	temp_tiles_rects = []
	tiles = pygame.sprite.Group()	
	entity_list = pygame.sprite.Group()
	projectiles = pygame.sprite.Group()
	weapon_pickups = pygame.sprite.Group()
	chests = pygame.sprite.Group()
	door_ways = pygame.sprite.Group()
	particles = pygame.sprite.Group()
	entity_list.add(player)
	
	

	#weapon_pickups.add(entities.WeaponPickup([200, 400], img_weapons[1], img_weapons[1].get_size(),
	#	 entities.Weapon(1, 500, None, 11, 3, img_bullets[0], img_weapons[1], 5)))

	dash_bar = ui.progress_bar((window.get_width() - 125, window.get_height() - 100), (100, 25), 1)
	mana_bar = ui.progress_bar((125, window.get_height() - 100), (100, 25), 1)
	mana_bar.set_color_main((10, 10, 255))
	mana_bar.set_color_background((10, 10, 10))
	health_bar = ui.progress_bar((125, window.get_height() - 50), (100, 25), 1)
	health_bar.set_color_main((255, 10, 10))
	health_bar.set_color_background((10, 10, 10))

	scene = 0

	clock = pygame.time.Clock()

	run = True

	play_button = ui.Button(200, 300, (200, 100), (255, 255, 255), img_play_button)
	scene_transition_timer_start = False
	scene_transition_timer_start_time = 0

	#for i in range(100):
	#	tiles.add(entities.Wall(((i * 10) * 32, i * 32), img_wall))

	while run:
		window.fill((20,20,20))
		pygame.display.set_caption(f'{1/(clock.tick(60) / 1000)}')

	
		if scene == 0:
			for event in pygame.event.get():
				if event.type == QUIT:
					run = False
				if event.type == MOUSEBUTTONDOWN:
					if event.button == 1:
						for i in range(10):
							offset = [random.randrange(-10, 10), random.randrange(-10, 10)]
							particles.add(entities.Particles([pygame.mouse.get_pos()[0] + offset[0], pygame.mouse.get_pos()[1] + offset[1]], [0,0], [0,0], 500))

			particles.update()

			

			draw_text("Main Menu", font, (255, 255, 255), (200, 200))
			draw_text('Controls', font, (255,255,255), (750, 200), True)
			draw_text('LMB : Shoot', font, (255,255,255), (750, 250), True)

			if play_button.draw(window):
				if not scene_transition_timer_start:
					scene_transition_timer_start_time = pygame.time.get_ticks()
				scene_transition_timer_start = True

				
				#scene = 1
				

			for p in particles:
				camera.render(p, window, BLEND_RGBA_ADD)

			if scene_transition_timer_start and pygame.time.get_ticks() > scene_transition_timer_start_time + 1000:
				scene = 1
				scene_transition_timer_start = False

		elif scene == 1:
			for event in pygame.event.get():
				if event.type == QUIT:
					run = False


				if event.type == MOUSEBUTTONDOWN:
					if event.button == 1:
						#player.attack(get_mouse_pos(), projectiles)
						pass
					

				if event.type == KEYDOWN:
					if event.key == K_w:
						player.moving[0] = True
					if event.key == K_s:
						player.moving[1] = True
					if event.key == K_a:
						player.moving[2] = True
					if event.key == K_d:
						player.moving[3] = True
					if event.key == K_q:
						player.drop(weapon_pickups)
					if event.key == K_SPACE:
						player.dash(particles)
				if event.type == KEYUP:
					if event.key == K_w:
						player.moving[0] = False
					if event.key == K_s:
						player.moving[1] = False
					if event.key == K_a:
						player.moving[2] = False
					if event.key == K_d:
						player.moving[3] = False

			if pygame.mouse.get_pressed()[0]:
				player.attack(get_mouse_pos(), projectiles)

			if player.dungeon_transition == True:
				player.dungeon_transition = False
				if gm.bm.draw_world:
					chests.empty()
					weapon_pickups.empty()
					gm.enterDungeon()
					entity_list.empty()
					entity_list.add(player)
					player.rect.center = (gm.dm.start_pos[0] * 64 + 32, gm.dm.start_pos[1] * 64 + 32)

				else:
					gm.exitDungeon()
					chests.empty()
					entity_list.empty()
					entity_list.add(player)
					weapon_pickups.empty()
					player.rect.center = (192, 192)
				

			#tiles.empty()
			temp_tiles.clear()
			temp_tiles_rects.clear()
			door_ways.empty()

			# for y in range(height // (CHUNK_SIZE * 32) + 3):
			# 	target_y = y - 1 + round(camera.pos[1] / (CHUNK_SIZE * 32))
			# 	for x in range(width // (CHUNK_SIZE * 32) + 3):
			# 		target_x = x - 1 + round(camera.pos[0] / (CHUNK_SIZE * 32))
			# 		target_chunk = str(target_x) + ';' + str(target_y)

			# 		if target_chunk not in game_map:
			# 			game_map[target_chunk] = generate_chunks(target_x, target_y)

			# 		for tile in game_map[target_chunk]:
			# 			if tile[1] in [1]:
			# 				#tiles.add(entities.Wall((tile[0][0] * 32, tile[0][1] * 32), img_wall))
			# 				temp_tiles[str(tile[0][0]) + ';' + str(tile[0][1])] = 1
			# 				temp_tiles_rects.append(pygame.Rect((tile[0][0] * 32, tile[0][1] * 32), (32, 32)))
			# 				window.blit(pygame.transform.scale(img_wall, (32, 32)), (tile[0][0] * 32 - camera.pos[0], tile[0][1] * 32 - camera.pos[1]))
			# 				pygame.draw.rect(window, (255, 255, 255), (temp_tiles_rects[-1].x - camera.pos[0], temp_tiles_rects[-1].y - camera.pos[1], 32, 32), 1)
			

			gm.bm.addToBoard(player.pos[0] // 64, player.pos[1] // 64)

			if gm.bm.draw_world:
				for tile in gm.bm.grid_positions:
					pos = gm.bm.grid_positions[tile][0]
					if pos[0] * 64 > camera.pos[0] - 128 and pos[0] * 64 < camera.pos[0] + camera.size[0] + 128 and pos[1] * 64 > camera.pos[1] - 128 and pos[1] * 64 < camera.pos[1] + camera.size[1] + 128:
						temp_tiles[tile] = gm.bm.grid_positions[tile][1]
						if temp_tiles[tile] == EMPTY:
							#print('here')
							window.blit(pygame.transform.scale(img_floor, (64, 64)), (gm.bm.grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.grid_positions[tile][0][1] * 64 - camera.pos[1]))
						elif temp_tiles[tile] == WALL:
							window.blit(pygame.transform.scale(img_wall, (64, 64)), (gm.bm.grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.grid_positions[tile][0][1] * 64 - camera.pos[1]))
							temp_tiles_rects.append(pygame.Rect((gm.bm.grid_positions[tile][0][0] * 64, gm.bm.grid_positions[tile][0][1] * 64), (64, 64)))
						elif temp_tiles[tile] == ENTERANCE:
							window.blit(pygame.transform.scale(img_floor, (64, 64)), (gm.bm.grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.grid_positions[tile][0][1] * 64 - camera.pos[1]))
							door_ways.add(entities.DoorWay((gm.bm.grid_positions[tile][0][0] * 64 + 32, gm.bm.grid_positions[tile][0][1] * 64 + 32), img_enterance, (64, 64)))
						elif temp_tiles[tile] == ENEMY:
							window.blit(pygame.transform.scale(img_floor, (64, 64)), (gm.bm.grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.grid_positions[tile][0][1] * 64 - camera.pos[1]))
							if random.randrange(0, 2) == 1:
								entity_list.add(entities.Melee_Enemy((gm.bm.grid_positions[tile][0][0] * 64, gm.bm.grid_positions[tile][0][1] * 64), img_cultist, player_ref = player, weapon = entities.Weapon(1, 250, None, 5, 300, img_bullets[0], img_weapons[0])))
							else:
								entity_list.add(entities.Ranged_Enemy((gm.bm.grid_positions[tile][0][0] * 64, gm.bm.grid_positions[tile][0][1] * 64), img_cultist, player_ref = player, weapon = entities.Weapon(1, 600, None, 1, 1000, img_bullets[1], img_weapons[0])))
							gm.bm.grid_positions[tile] = [pos, EMPTY]


			else:
				for tile in gm.bm.dungeon_grid_positions:	
					pos = gm.bm.dungeon_grid_positions[tile][0]
					if pos[0] * 64 > camera.pos[0] - 128 and pos[0] * 64 < camera.pos[0] + camera.size[0] + 128 and pos[1] * 64 > camera.pos[1] - 128 and pos[1] * 64 < camera.pos[1] + camera.size[1] + 128:			
						temp_tiles[tile] = gm.bm.dungeon_grid_positions[tile][1]
						#print(gm.bm.dungeon_grid_positions[tile])
						if temp_tiles[tile] == EMPTY:
							#print('here')
							window.blit(pygame.transform.scale(img_floor, (64, 64)), (gm.bm.dungeon_grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.dungeon_grid_positions[tile][0][1] * 64 - camera.pos[1]))
						elif temp_tiles[tile] == WALL:
							window.blit(pygame.transform.scale(img_wall, (64, 64)), (gm.bm.dungeon_grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.dungeon_grid_positions[tile][0][1] * 64 - camera.pos[1]))
							temp_tiles_rects.append(pygame.Rect((gm.bm.dungeon_grid_positions[tile][0][0] * 64, gm.bm.dungeon_grid_positions[tile][0][1] * 64), (64, 64)))
						elif temp_tiles[tile] == OUTERWALL:
							window.blit(pygame.transform.scale(img_wall, (64, 64)), (gm.bm.dungeon_grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.dungeon_grid_positions[tile][0][1] * 64 - camera.pos[1]))
							temp_tiles_rects.append(pygame.Rect((gm.bm.dungeon_grid_positions[tile][0][0] * 64, gm.bm.dungeon_grid_positions[tile][0][1] * 64), (64, 64)))
						elif temp_tiles[tile] == CHEST:
							window.blit(pygame.transform.scale(img_floor, (64, 64)), (gm.bm.dungeon_grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.dungeon_grid_positions[tile][0][1] * 64 - camera.pos[1]))
							if random.randrange(0, 5) == 1:
								chests.add(entities.Health_Chest((gm.bm.dungeon_grid_positions[tile][0][0] * 64 + 32, gm.bm.dungeon_grid_positions[tile][0][1] * 64 + 32), img_chest_closed, img_chest_open, (64,64), img_health_pickup))
							else:
								chests.add(entities.Weapons_Chest((gm.bm.dungeon_grid_positions[tile][0][0] * 64 + 32, gm.bm.dungeon_grid_positions[tile][0][1] * 64 + 32), img_chest_closed, img_chest_open, (64,64), img_weapons, img_bullets))
							gm.bm.dungeon_grid_positions[tile] = [pos, EMPTY]
						elif temp_tiles[tile] == ENEMY:
							window.blit(pygame.transform.scale(img_floor, (64, 64)), (gm.bm.dungeon_grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.dungeon_grid_positions[tile][0][1] * 64 - camera.pos[1]))
							
							if random.randrange(0,2) == 1:
								entity_list.add(entities.Melee_Enemy((gm.bm.dungeon_grid_positions[tile][0][0] * 64, gm.bm.dungeon_grid_positions[tile][0][1] * 64), img_cultist, player_ref = player, weapon = entities.Weapon(1, 250, None, 5, 300, img_bullets[0], img_weapons[0])))
							else:
								entity_list.add(entities.Ranged_Enemy((gm.bm.dungeon_grid_positions[tile][0][0] * 64, gm.bm.dungeon_grid_positions[tile][0][1] * 64), img_cultist, player_ref = player, weapon = entities.Weapon(1, 600, None, 1, 1000, img_bullets[1], img_weapons[0])))
							gm.bm.dungeon_grid_positions[tile] = [pos, EMPTY]
						elif temp_tiles[tile] == EXIT:
							window.blit(pygame.transform.scale(img_floor, (64, 64)), (gm.bm.dungeon_grid_positions[tile][0][0] * 64 - camera.pos[0], gm.bm.dungeon_grid_positions[tile][0][1] * 64 - camera.pos[1]))
							door_ways.add(entities.DoorWay((gm.bm.dungeon_grid_positions[tile][0][0] * 64 + 32, gm.bm.dungeon_grid_positions[tile][0][1] * 64 + 32), img_exit, (64, 64)))

				#print(len(temp_tiles_rects))
	
			
			
			for i, e in sorted(enumerate(entity_list), reverse = True):
				if e.alive:
					e.update(temp_tiles_rects, entity_list, projectiles, particles, get_mouse_pos())
					camera.render(e, window)
				else:
					entity_list.remove(e)

			#pygame.draw.rect(window, (255, 0, 0), pygame.Rect((player.rect.x + player.v[0] - camera.pos[0], player.rect.y - camera.pos[1]), player.rect.size), 1)
			

			#print(e2.pos[0] - player.pos[0], e2.pos[1] - player.pos[1])

		
			#print(len(projectiles))
			for i, p in sorted(enumerate(projectiles), reverse = True):
				#print(p)
				if p.alive:
					p.update(temp_tiles, entity_list, weapon_pickups, particles)
					image = pygame.Surface((24, 24))
					image.fill((100, 100, 100))
					temp_image = pygame.Surface((24, 24))
					pygame.draw.circle(temp_image, p.color, (12, 12), 4 + 8 * abs(math.cos(((pygame.time.get_ticks() - p.life_start - random.randrange(0, 200)) / 200))))
					image.set_colorkey((0,0,0))
					image.blit(temp_image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
					window.blit(image, (p.pos[0] - camera.pos[0] - 12, p.pos[1] - camera.pos[1] - 12), special_flags =  BLEND_RGBA_ADD)
					camera.render(p, window)
					
				else:
					p.kill()

			particles.update()

			for p in particles:
				camera.render(p, window, BLEND_RGBA_ADD)

			
			
			for d in door_ways:
				d.update(player, gm)
				camera.render(d, window)
			for c in chests:
				c.update(player, weapon_pickups)
				camera.render(c, window)
			for wp in weapon_pickups:
				wp.update(entity_list, projectiles, particles, weapon_pickups)
				camera.render(wp, window)
			#pygame.draw.circle(window, (COL_DEBUG),(player.rect.x - camera.pos[0], player.rect.y - camera.pos[1]), 20)

		
			camera.set_pos((player.rect.bottomright[0] - camera.renderRect.width // 2 + player.rect.w, player.rect.bottomright[1] - camera.renderRect.height // 2 + player.rect.h))
			

		
			for tile in tiles:
				tile.draw(window, camera)
			
			pygame.draw.line(window, (20, 20, 20), (0,0), (0, height - 1), 5)
			pygame.draw.line(window, (20, 20, 20), (0,0), (width - 1, 0), 5)
			pygame.draw.line(window, (20, 20, 20), (width - 1, 0), (width - 1, height - 1), 5)
			pygame.draw.line(window, (20, 20, 20), (0, height - 1), (width - 1, height - 1), 5)

			#pygame.draw.line(window, (20, 20, 20), (width// 2, 0), (width // 2, height - 1), 5)	
			#pygame.draw.line(window, (20, 20, 20), (0, height // 2), (width, height // 2), 5)		
			

			enemy_list = []

			for e in entity_list:
				if isinstance(e, entities.Enemy):
					enemy_list.append(e)


			draw_text(f'Dash Timer: ', font, (255,255,255), (window.get_width() - 350, window.get_height() - 100))
			draw_text(f'Mana: ', font, (255,255,255), (20, window.get_height() - 100))
			draw_text(f'Health: ', font, (255,255,255), (20, window.get_height() - 50))
			#print(min(1, (pygame.time.get_ticks() - player.last_dash) / player.dash_cooldown))
			dash_bar.set_v(min(1, (pygame.time.get_ticks() - player.last_dash) / player.dash_cooldown))
			mana_bar.set_v(min(1, (player.mana / player.max_mana)))
			health_bar.set_v(min(1, (player.health / player.max_health)))
			dash_bar.draw(window)
			mana_bar.draw(window)
			health_bar.draw(window)

			#if len(enemy_list) == 0:
			#	draw_text('Level Complete', font, (255,255,255), (window.get_width() // 2, window.get_height() // 2), True)


		screen.blit(pygame.transform.scale(window, (screen.get_width(), screen.get_height())), (0,0))
		pygame.display.update()



if __name__ == '__main__':
	main()