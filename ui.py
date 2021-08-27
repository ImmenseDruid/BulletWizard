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

	def set_color_main(self, color):
		self.col_1 = color 
	def set_color_background(self, color):
		self.col_2 = color

	def draw(self, screen):
		img = pygame.Surface(self.size)
		img.set_colorkey((0,0,0))
		pygame.draw.rect(img, self.col_2, self.r2)
		pygame.draw.rect(img, self.col_1, self.r1)
		
		screen.blit(img, self.pos, special_flags = BLEND_RGBA_ADD)

class Button():

	HOVER_COL = (200, 200, 200)
	CLICKED_COL = (0, 0, 0)
	ACTION_COL = (255, 255, 255)
	DISABLED_COL = (50, 0, 0)


	def __init__(self, x, y, size, color = (0, 100, 0), img = None, scale = 1):

		self.x = x
		self.y = y

		
		self.color = color

		self.clicked = False
		self.enabled = True
		self.hovered = False

		if img:
			self.img = img
			imgSize = [img.get_rect().w * scale, img.get_rect().h * scale]
			
			self.size = (imgSize[0], imgSize[1])
			surf = pygame.Surface(self.size)
			pygame.draw.rect(surf, color, pygame.Rect((0, 0), self.size))
		else:
			surf = pygame.Surface((size[0], size[1]))
			pygame.draw.rect(surf, color, pygame.Rect((0, 0), (size)))
			self.img = surf
			self.size = size

	def set_pos(self, x, y):
		self.x = x 
		self.y = y 

	def set_color(self, hover, clicked, action, base):		self.color = base

	def draw(self, screen):

		rect = pygame.Rect((self.x, self.y), self.size)
		pos = pygame.mouse.get_pos()

		
		col = self.color



		action = False

		surf = pygame.Surface((self.size[0], self.size[1]))
		#Blit image to button
		surf.blit(self.img, (self.size[0] // 2 - self.img.get_rect().w // 2 , self.size[1] // 2 - self.img.get_rect().h // 2))
		coloring_surface = pygame.Surface(self.size)

		self.hovered = rect.collidepoint(pos)


		if self.hovered and self.enabled:
			
			if pygame.mouse.get_pressed()[0] == 1:
				self.clicked = True
				col = self.CLICKED_COL
				pygame.draw.rect(coloring_surface, (0, 0, 0), ((0,0), self.size))
				
				
 
			if pygame.mouse.get_pressed()[0] == 0 and not self.clicked:
				col = self.HOVER_COL
				pygame.draw.rect(coloring_surface, (100,100,100), ((0,0), self.size))
				


			if pygame.mouse.get_pressed()[0] == 0 and self.clicked:
				action = True
				self.clicked = False
				col = self.ACTION_COL
				pygame.draw.rect(coloring_surface, (250,250,250), ((0,0), self.size))
		

		if False:
			#Create Border
			
			pygame.draw.rect(surf, col, pygame.Rect(0, 0, self.size[0] + 4, self.size[1] + 4))

		surf.blit(coloring_surface, (0,0), special_flags = BLEND_RGB_ADD)

		if not self.enabled:
			red_coloring = pygame.Surface(self.size)
			pygame.draw.rect(red_coloring, (255, 0, 0), ((0,0), (self.size)))
			red_coloring.set_colorkey((0,0,0))
			surf.blit(red_coloring, (0,0), special_flags = BLEND_RGB_ADD)

		screen.blit(surf, (self.x, self.y))
		return action
