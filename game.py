import pygame, entities, ui
import math, random
import numpy as np
import os
from pygame.locals import *


pygame.init()

font = pygame.font.SysFont('Courier New', 30)

COL_DEBUG = (255, 0, 255)
scale = 2
width = 600
height = 600
camera = entities.Camera((width, height))
screen = pygame.display.set_mode((width * scale, height * scale))
window = pygame.Surface((width, height))


def draw_text(text, font, color, pos):
	img = font.render(text, True, color)
	window.blit(img, pos)

img_wall = pygame.image.load(os.path.join('Images', 'wall.png')).convert()
img_floor = pygame.image.load(os.path.join('Images', 'floor.png')).convert()
img_bullet = pygame.image.load(os.path.join('Images', 'base_projectile.png')).convert_alpha()
img_player = pygame.image.load(os.path.join('Images', 'player.png')).convert_alpha()
img_cultist = pygame.image.load(os.path.join('Images', 'cultist.png')).convert_alpha()
img_weapons = [pygame.image.load(os.path.join('Images', 'staff_1.png')).convert_alpha(), pygame.image.load(os.path.join('Images', 'staff_2.png')).convert_alpha()]

tile_index = {1 : img_wall}

def get_mouse_pos():
	return (pygame.mouse.get_pos()[0] // scale + camera.pos[0], pygame.mouse.get_pos()[1] // scale + camera.pos[1])

CHUNK_SIZE = 32

floor_map = []

for i in range(width // 32 + 3):
	floor_map.append([])
	for j in range(height // 32 + 4):
		floor_map[i].append([i * 32, j * 32])

#TODO : 
#  : WEDNESDAY : FIX DUPLICATION BUG, CREATE MORE ENEMIES / BETTER ENEMY AI (STEERING BEHAVIORS, WITH WEIGHTED CHOICE), CREATE BOSS, CREATE MORE WEAPONS, CREATE SHIELD BURST (PUSH PROJECTILES AWAY), CHANGE DROP TO Q, CREATE SPECIAL POWERS??? (TURN SHIELD BURST INTO OTHER THINGS MAYBE OR JUST MORE POWERS THAT YOU CAN BUY AND STUFF)
#  : THURSDAY : CREATE BETTER MAP GENERATION, CREATE ROOM CREATOR, MAPS WILL GENERATE HANDMADE ROOMS ALONG A PATH, EVENTUALLY LEADING TO ITEM ROOMS, A SHOP, AND A BOSS
#  : FRIDAY : POLISH POLISH POLISH
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
			if noise[x_pos] < 0.5:
				tile_type = 0
			elif noise[x_pos] > 0.5:
				tile_type = 1

			tiles.append([[target_x, target_y], tile_type])
		chunk.append(tiles)
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

def main():


	player = entities.Player([100, 100], img_player)
	wp = entities.Weapon(1, 400, player, 3, 150, img_bullet, img_weapons[0])
	player.weapon = wp


	e1 = entities.Melee_Enemy([500, 200], img_cultist, player_ref = player)
	w1 = entities.Weapon(1, 250, e1, 5, 300, img_bullet, img_weapons[0])
	e1.weapon = w1
	e2 = entities.Ranged_Enemy([300, 0], img_cultist, player_ref = player)
	w2 = entities.Weapon(1, 600, e2, 1, 1000, img_bullet, img_weapons[0])
	e2.weapon = w2

	#500 -> 300
	#250 -> 150

	game_map = {}
	tiles = pygame.sprite.Group()	
	entity_list = pygame.sprite.Group()
	projectiles = pygame.sprite.Group()
	particles = pygame.sprite.Group()
	entity_list.add(player)
	#entity_list.add(e1)
	#entity_list.add(e2)

	entity_list.add(entities.WeaponPickup([200, 400], img_weapons[1], img_weapons[1].get_size(),
		 entities.Weapon(1, 500, None, 11, 3, img_bullet, img_weapons[1])))

	dash_bar = ui.progress_bar((window.get_width() - 125, window.get_height() - 100), (100, 25), 1)

	scene = 1

	clock = pygame.time.Clock()

	run = True

	#for i in range(100):
	#	tiles.add(entities.Wall(((i * 10) * 32, i * 32), img_wall))

	while run:
		window.fill((20,20,20))
		pygame.display.set_caption(f'{1/(clock.tick(60) / 1000)}')

		for i in range(len(floor_map)):
			for j in range(len(floor_map[i])):
				if floor_map[i][j][0] < camera.pos[0] - 96:
					floor_map[i][j][0] += width - 4 + 96
				elif floor_map[i][j][0] > camera.pos[0] + camera.size[0] + 64:
					floor_map[i][j][0] -= width - 4 + 96
				if floor_map[i][j][1] < camera.pos[1] - 96:
					floor_map[i][j][1] += height - 4 + 96
				elif floor_map[i][j][1] > camera.pos[1] + camera.size[1] + 64:
					floor_map[i][j][1] -= height - 4 + 96
				window.blit(img_floor, (floor_map[i][j][0] - camera.pos[0], floor_map[i][j][1] - camera.pos[1]))
		
		

		if scene == 1:
			for event in pygame.event.get():
				if event.type == QUIT:
					run = False

				if event.type == MOUSEBUTTONDOWN:
					if event.button == 1:
						#player.attack(get_mouse_pos(), projectiles)
						pass
					if event.button == 3:
						player.drop(entity_list)

				if event.type == KEYDOWN:
					if event.key == K_w:
						player.moving[0] = True
					if event.key == K_s:
						player.moving[1] = True
					if event.key == K_a:
						player.moving[2] = True
					if event.key == K_d:
						player.moving[3] = True

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

			tiles.empty()
			
			for y in range(height // (CHUNK_SIZE * 32) + 2):
				target_y = y - 1 + round(camera.pos[1] / (CHUNK_SIZE * 32))
				for x in range(width // (CHUNK_SIZE * 32) + 2):
					target_x = x - 1 + round(camera.pos[0] / (CHUNK_SIZE * 32))
					target_chunk = str(target_x) + ';' + str(target_y)

					if target_chunk not in game_map:
						game_map[target_chunk] = generate_chunks(target_x, target_y)

					for tile in game_map[target_chunk]:

						if tile[1] in [1]:
							tiles.add(entities.Wall((tile[0][0] * 32, tile[0][1] * 32), img_wall))

				#print(game_map)

			
			
			for i, e in enumerate(entity_list):
				if e.alive:
					e.update(tiles, entity_list, projectiles, particles, get_mouse_pos())
					camera.render(e, window)
				else:
					entity_list.remove(e)

			#projectiles.update	()
			#print(len(projectiles))
			for p in projectiles:

				if p.alive:
					p.update(tiles, entity_list, particles)

					image = pygame.Surface((24, 24))
					image.fill((100, 100, 100))
					temp_image = pygame.Surface((24, 24))
					pygame.draw.circle(temp_image, (99, 155, 205), (12, 12), 4 + 8 * abs(math.cos(((pygame.time.get_ticks() - p.life_start - random.randrange(0, 200)) / 200))))
					image.set_colorkey((0,0,0))
					image.blit(temp_image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
					window.blit(image, (p.pos[0] - camera.pos[0] - 12, p.pos[1] - camera.pos[1] - 12), special_flags =  BLEND_RGBA_ADD)
					camera.render(p, window)
					
				else:
					p.kill()

			particles.update()

			for p in particles:
				camera.render(p, window, BLEND_RGBA_ADD)

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
			#print(min(1, (pygame.time.get_ticks() - player.last_dash) / player.dash_cooldown))
			dash_bar.set_v(min(1, (pygame.time.get_ticks() - player.last_dash) / player.dash_cooldown))
			dash_bar.draw(window)

			if len(enemy_list) == 0:
				draw_text('Level Complete', font, (255,255,255), (window.get_width() // 2, window.get_height() // 2))


		screen.blit(pygame.transform.scale(window, (screen.get_width(), screen.get_height())), (0,0))
		pygame.display.update()



if __name__ == '__main__':
	main()