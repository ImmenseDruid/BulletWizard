from pydub import AudioSegment
import pygame
from pydub.playback import play
import os, sys
import math, numpy
import itertools
from scipy import interpolate
from operator import itemgetter

pygame.init()

screen = pygame.display.set_mode((200, 200))

pygame.mixer.init()
file = AudioSegment.from_file(file = os.path.join(os.path.join('Sounds', 'Music'), 'Dubstep.ogg'), format='ogg')
length = 153.787 * 1000
start = file[:3000]
file_without_end = file[:length - 3000]
loop = file_without_end.overlay(start.reverse(), position = 147 * 1000)
print(file.duration_seconds)


loop.export('Sounds\\Music\\dubstep1.ogg', format = 'ogg')

wood = pygame.mixer.Sound('Sounds\\Music\\dubstep1.ogg')
wood.set_volume(0.1)


while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

		if event.type == pygame.MOUSEBUTTONDOWN:
			wood.play()



wood.play()

