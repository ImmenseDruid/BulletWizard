import pygame
from pygame.locals import *

class progress_bar ():
	def __init__(self, pos, size, v):
		self.pos = pos 
		self.size = size
		self.value = v 
		self.col_1 = (255, 255, 255)
		self.col_2 = (100, 100, 100)
		self.r1 = pygame.Rect((0,0), (self.size[0] * v, self.size[1]))
		self.r2 = pygame.Rect((self.size[0] * v, 0), (self.size[0] * (1-v), self.size[1]))

	def set_v(self, v):
		self.value = v 
		self.r1 = pygame.Rect((0,0), (self.size[0] * v, self.size[1]))
		self.r2 = pygame.Rect((0, 0), (self.size[0], self.size[1]))

	def draw(self, screen):
		img = pygame.Surface(self.size)
		img.set_colorkey((0,0,0))
		pygame.draw.rect(img, self.col_2, self.r2)
		pygame.draw.rect(img, self.col_1, self.r1)
		
		screen.blit(img, self.pos, special_flags = BLEND_RGBA_ADD)