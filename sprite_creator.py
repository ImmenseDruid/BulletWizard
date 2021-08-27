import pygame, os
from pygame.locals import *
pygame.init()
run = True
screen = pygame.display.set_mode((800, 900))

staff_path = os.path.join('Images', 'Staff')

bases = []
holders = []
orbs = []

base_path = os.path.join(staff_path, 'Base')
for file in os.listdir(base_path):
	surf = pygame.image.load(os.path.join(base_path, file)).convert_alpha()
	surf.set_colorkey((0,0,0))
	bases.append(surf)

holder_path = os.path.join(staff_path, 'Holder')
for file in os.listdir(holder_path):
	surf = pygame.image.load(os.path.join(holder_path, file)).convert_alpha()
	surf.set_colorkey((0,0,0))
	holders.append(surf)

orb_path = os.path.join(staff_path, 'Orbs')
for file in os.listdir(orb_path):
	surf = pygame.image.load(os.path.join(orb_path, file)).convert_alpha()
	surf.set_colorkey((0,0,0))
	orbs.append(surf)

staffs = []

for i in range(len(bases)):
	for j in range(len(holders)):
		for k in range(len(orbs)):
			surf = pygame.Surface((32, 32), SRCALPHA)
			surf.set_colorkey((0,0,0))
			surf.blit(orbs[k], (0,0))
			surf.blit(bases[i], (0,0))
			surf.blit(holders[j], (0,0))
			surf.set_colorkey((0,0,0))
			staffs.append(surf)

for i, staff in enumerate(staffs):
	pygame.image.save(staff, os.path.join(staff_path, f'{i}.png'))


while run:

	screen.fill((50,50,50))

	for event in pygame.event.get():
		if event.type == QUIT:
			run = False
	
	for i in range(len(bases)):
		screen.blit(bases[i], (i * 32, 32))
	for i in range(len(holders)):
		screen.blit(holders[i], (i * 32, 64))
	for i in range(len(orbs)):
		screen.blit(orbs[i], (i * 32, 100))

	for i in range(len(staffs)):
		screen.blit(staffs[i], ((i * 32) % 800, 132 + (i * 32) // 800 * 32))


	pygame.display.update()