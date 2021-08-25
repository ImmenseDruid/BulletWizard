import math, random
import numpy as np
import timeit

CHUNK_SIZE = 8
width = 900
height = 500
game_map = {}
player_x = 0
player_y = 0
tiles = []

def game_test():
	global player_x, player_y
	player_x += 1 
	player_y += 1
	map_lookup([player_x, player_y])

def map_lookup(cam_pos):

	for y in range(height // (CHUNK_SIZE * 32) + 2):
		target_y = y - 1 + round(cam_pos[1] / (CHUNK_SIZE * 32))
		for x in range(width // (CHUNK_SIZE * 32) + 2):
			target_x = x - 1 + round(cam_pos[0] / (CHUNK_SIZE * 32))
			target_chunk = str(target_x) + ';' + str(target_y)

			if target_chunk not in game_map:
				game_map[target_chunk] = generate_chunks(target_x, target_y)

			for tile in game_map[target_chunk]:
				if tile[1] in [1]:
					tiles.append((25, 25, 25, 25))


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

					if walls >= 3:
						chunk[j][i][1] = 1
					else:
						chunk[j][i][1] = 0

	
	#print(chunk)


	
	biome = 0
	chunck_data = []
	for j in range(len(chunk)):
		for i in range(len(chunk[j])):
			if chunk[j][i][1] != 0:	
				chunck_data.append(chunk[j][i])

	#print(chunck_data)

	return chunck_data

if __name__ == '__main__':
	s = 0
	for i in range(100):
		s += timeit.timeit('game_test()', setup = "from __main__ import game_test", number = 1000)

	print(s)
	print(s / 100)
	print(s / 100000)
	print(100000 / 4200)