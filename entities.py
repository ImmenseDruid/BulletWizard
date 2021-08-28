import pygame, math, random
import numpy as np

def distSqr(p1, p2):
	return ((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))

def get_angle_to_pos(startpos, endpos):
	x_dist = startpos[0] - endpos[0]
	y_dist = -(startpos[1] - endpos[1])
	return math.degrees(math.atan2(y_dist, x_dist))

def lerp(v1, v2, x):
	return (v2 * x) + ((1-x) * v1)

def limit(x, y, z):
	if z < y:
		z = y 
	if z > x:
		z = x 

	return z

def alerp(v1, v2, x):
	x = limit(v1, v2, x)

	return (v2 - x) / (x + v1)


class Camera():
	def __init__(self, size):
		self.pos = [0,0]
		self.size = size
		self.renderRect = pygame.Rect(self.pos, (size[0] + 100, size[1] + 100))
		self.loaderRect = pygame.Rect((self.pos[0] - size[0], self.pos[1] - size[1]), (size[0] * 3, size[1] * 3))

	def resize(self, size):
		self.size = size
		self.renderRect = pygame.Rect(self.pos, (size[0] + 100, size[1] + 100))
		self.loaderRect = pygame.Rect((self.pos[0] - size[0], self.pos[1] - size[1]), (size[0] * 3, size[1] * 3))

	def move(self, v):
		self.pos[0] += v[0]
		self.pos[1] += v[1]

		self.renderRect.x = self.pos[0]
		self.renderRect.y = self.pos[1]

	def set_pos(self, pos):
		self.pos = (pos[0], pos[1]) 
		self.renderRect.x = self.pos[0] - 50
		self.renderRect.y = self.pos[1] - 50
		self.loaderRect.x = self.pos[0] - self.renderRect.w 
		self.loaderRect.y = self.pos[1] - self.renderRect.h

	def render(self, entity, window, special_flags = 0):
		if entity.rect.colliderect(self.renderRect):
			window.blit(entity.image, (entity.pos[0] - self.pos[0] - entity.image.get_width() // 2 , entity.pos[1] - self.pos[1] - entity.image.get_height() // 2), special_flags = special_flags)

		if entity.rect.colliderect(self.loaderRect):
			entity.enabled = True
		else:
			entity.enabled = False
	


# class Static_Entity(pygame.sprite.Sprite):
# 	def __init__(self, pos, img = None, size = (32, 32)):
# 		pygame.sprite.Sprite.__init__(self)

# 		if not img:
# 			img = pygame.Surface(size)
# 			pygame.draw.rect(img, (0, 0, 255), ((0,0), size))

# 		img = pygame.transform.scale(img, size)

# 		self.pos = pos
# 		self.image = img
# 		self.size = size
# 		self.rect = pygame.Rect(pos, self.size)
# 		self.enabled = True

# 	def collide(self, entity):
# 		pass


# 	def draw(self, screen, camera):
# 		screen.blit(self.image, (self.rect.x - camera.pos[0], self.rect.y - camera.pos[1]))

# class Wall(Static_Entity):
# 	def __init__(self, pos, img = None, size = (32, 32)):
# 		super().__init__(pos, img, size)

# 	def collide(self, entity):
# 		super().collide(entity)
			

# 	class Spiked_Wall(Static_Entity):
# 		def __init__(self, pos, img = None, size = (32, 32)):
# 			super().__init__(pos, img, size)

# 		def collide(self, entity):
# 			super().collide(entity)
# 			entity.damage(1)

class Entity(pygame.sprite.Sprite):
	def __init__(self, pos, img = None, size = (32, 32)):
		pygame.sprite.Sprite.__init__(self)

		if not img:
			img = pygame.Surface(size)
			pygame.draw.rect(img, (0, 255, 255), ((0,0), size))

		img = pygame.transform.scale(img, size)

		self.v = [0, 0]
		self.a = [0, 0]
		self.mass = 10
		self.forces = []
		self.pos = pos
		self.moving = [False, False, False, False]

		self.weapon = None

		self.image = img
		self.img = self.image
		self.size = size
		self.rect = pygame.Rect(pos, self.size)
		self.rect.topleft = (pos[0] - self.img.get_width() // 2, pos[1] - self.img.get_height() // 2)
		self.enabled = True
		self.alive = True
		self.health = 1

		self.mana = 100 
		self.max_mana = 100
		self.mana_regen_cooldown = 1000

		self.dash_cooldown = 2000
		self.last_dash = -2000

		self.inventory = [None, None, None, None, None]

	def update(self, *args):
		if self.enabled:
			if self.alive:
				
				if self.weapon:
					if pygame.time.get_ticks() > self.weapon.fired_last + self.mana_regen_cooldown:
						self.mana = min(self.mana + 1, self.max_mana)

				self.v[0] += self.a[0]
				self.v[1] += self.a[1]

				if False:
					if self.v[0] != 0 or self.v[1] != 0:
						self.v[0] = self.v[0] * abs(self.v[0]) / ((self.v[0] * self.v[0]) + (self.v[1] * self.v[1]))
						self.v[1] = self.v[1] * abs(self.v[1]) / ((self.v[0] * self.v[0]) + (self.v[1] * self.v[1]))
						self.v[0] *= self.speed
						self.v[1] *= self.speed


				dx = self.v[0]
				dy = self.v[1]

				dx, dy = self.collide(dx, dy, args[0], args[1], args[3])

				

				self.rect.centerx += dx
				self.rect.centery += dy

				self.pos = self.rect.center
				#self.rect.y = self.pos[1]

	def collide(self, dx, dy, tiles, entity_list, particles):
		#loc_str = str(int((self.pos[0] + dx) //	32)) + ';' + str(int((self.pos[1] + dy) // 32))
		
		for t in tiles:

			if t.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
				#t.collide(self)
				if self.v[0] < 0:
					dx =t.x + t.w - self.rect.x
				elif self.v[0] > 0:
					dx = t.x - self.rect.w - self.rect.x

				self.v[0] = 0
			if t.colliderect(pygame.Rect((self.rect.x, self.rect.y + dy), self.rect.size)):
				#t.collide(self)
				if self.v[1] < 0:
					dy = t.y + t.h - self.rect.y
				elif self.v[1] > 0:
					dy = t.y - self.rect.h - self.rect.y

				self.v[1] = 0

		for e in entity_list:
			if e != self:
				if e.rect.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
					self.collide_with(e, entity_list, particles)
					if self.v[0] < 0:
						dx = e.rect.x + e.rect.w - self.rect.x
					elif self.v[0] > 0:
						dx = e.rect.x - self.rect.w - self.rect.x

					self.v[0] = 0
				if e.rect.colliderect(pygame.Rect((self.rect.x, self.rect.y + dy), self.rect.size)):
					self.collide_with(e, entity_list, particles)
					if self.v[1] < 0:
						dy = e.rect.y + e.rect.h - self.rect.y
					elif self.v[1] > 0:
						dy = e.rect.y - self.rect.h - self.rect.y

					self.v[1] = 0
		
		return dx, dy

	def collide_with(self, *args):
		#print(type(args[0]))

		if isinstance(args[0], Projectile):
			self.damage(1)
			for i in range(10):
				offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
				args[2].add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (255, 0, 0)))
		elif isinstance(args[0], Enemy) or isinstance(args[0], Player):
			args[0].damage(1)
			for i in range(10):
				offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
				args[2].add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (255, 0, 0)))		
			self.damage(1)

		# elif isinstance(args[0], WeaponPickup): 
		# 	self.drop(args[1])
		# 	self.weapon = args[0].weapon
		# 	self.weapon.owner = self
		# 	for i in range(10):
		# 		offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
		# 		args[2].add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (255, 255, 255)))
		# 	args[0].kill()
		# 	#del args[0]
			
	def heal(self, amount):
		self.health += amount

	def damage(self, amount):
		self.health -= amount
		if self.health <= 0:			
			self.alive = False

	def attack(self, pos, projectiles):
		if self.alive and self.enabled:
			if self.weapon and self.mana > self.weapon.mana_cost:
				if pygame.time.get_ticks() >= self.weapon.fired_last + self.weapon.cooldown:
					x_dist = pos[0] - self.rect.center[0]
					y_dist = -(pos[1] - self.rect.center[1])
					angle = math.degrees(math.atan2(y_dist, x_dist))
					force_angle = math.radians(math.degrees(math.atan2(y_dist, x_dist)) + 180)

					force = 2

					self.v[0] += math.cos(force_angle) * force
					self.v[1] += -math.sin(force_angle) * force
					self.mana = max(0, self.mana - self.weapon.mana_cost)
					self.weapon.attack(pos, projectiles, angle)

	
	def dash(self, particles):
		if pygame.time.get_ticks() > self.last_dash + self.dash_cooldown:
			mag = math.sqrt(distSqr((0,0), self.v))
			if mag > 0:			
				self.last_dash = pygame.time.get_ticks()
				
				direction = (self.v[0] / mag, self.v[1] / mag)
				self.v = [self.speed * 20 * direction[0], self.speed * 20 * direction[1]]

				for i in range(10):
					offset = [random.randrange(-10, 10), random.randrange(-10, 10)]
					particles.add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500))

	def pickup(self, weapon, pickup_list):
		self.drop_weapon(pickup_list)
		self.weapon = weapon
		self.weapon.owner = self

	def drop_weapon(self, pickup_list):
		#print('weapon : ' + str(self.weapon))
		if self.weapon is not None:
			self.weapon.drop(pickup_list)
			self.weapon = None

	#def equip(self, item, pickup_list):


	def draw(self, screen):
		screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(Entity):
	def __init__(self, pos, img = None, size = (32, 32)):
		if not img:
			img = pygame.Surface(size)
			pygame.draw.rect(img, (255, 255, 255), ((0,0), size))
		super().__init__(pos, img, size)
		
		self.dungeon_transition = False
		self.speed = 2
		self.health = 10
		self.max_health = 10
		

	def update(self, *args):	

		self.image = pygame.transform.rotate(self.img, get_angle_to_pos(self.rect.center, args[4]) + 90)

		if abs(self.v[0]) <= .1:
			self.v[0] = 0
		if abs(self.v[1]) <= .1:
			self.v[1] = 0

		self.a = [-self.v[0] / 5, -self.v[1] / 5]

		if self.moving[0]:
			self.moveUp()
		if self.moving[1]:
			self.moveDown()
		if self.moving[2]:
			self.moveLeft()
		if self.moving[3]:
			self.moveRight()

		super().update(args[0], args[1], args[2], args[3])

	def damage(self, amount):
		self.health -= amount
		if self.health <= 0:			
			self.alive = False

	def moveUp(self):
		self.v[1] -= self.speed
	def moveDown(self):
		self.v[1] += self.speed
	def moveLeft(self):
		self.v[0] -= self.speed
	def moveRight(self):
		self.v[0] += self.speed

class Enemy(Entity):
	def __init__(self, pos, img = None, size = (32, 32), player_ref = None):
		if not img:
			img = pygame.Surface(size)
			pygame.draw.rect(img, (255, 0, 0), ((0,0), size))

		self.speed = 1
		self.player_ref = player_ref
		self.sight_radius = 500 * 500
		self.desired_pos = None
		super().__init__(pos, img, size)

	def update(self, *args):
		if abs(self.v[0]) <= .1:
			self.v[0] = 0
		if abs(self.v[1]) <= .1:
			self.v[1] = 0

		self.a = [-self.v[0] / 5, -self.v[1] / 5]

		if self.moving[0]:
			self.moveUp()
		if self.moving[1]:
			self.moveDown()
		if self.moving[2]:
			self.moveLeft()
		if self.moving[3]:
			self.moveRight()

		super().update(args[0], args[1], args[2], args[3])


	
	def moveUp(self):
		self.v[1] -= self.speed
	def moveDown(self):
		self.v[1] += self.speed
	def moveLeft(self):
		self.v[0] -= self.speed
	def moveRight(self):
		self.v[0] += self.speed

class Melee_Enemy(Enemy):
	def __init__(self, pos, img = None, size = (32, 32), player_ref = None, weapon = None):
		super().__init__(pos, img, size, player_ref)
		self.weights = []
		self.speed = 2
		self.weapon = weapon
		self.weapon.owner = self


	def update(self, *args):
		super().update(args[0], args[1], args[2], args[3])

		self.image = pygame.transform.rotate(self.img, get_angle_to_pos(self.rect.topleft, self.player_ref.rect.center) + 90)

		for m in range(len(self.moving)):
			self.moving[m] = False

		dist_to_player = distSqr(self.player_ref.rect.center, self.rect.center)

		
		if dist_to_player < self.sight_radius:
			self.desired_pos = self.player_ref.rect.center
		else:
			self.desired_pos = (self.rect.centerx + random.randint(-20, 20), self.rect.centery + random.randint(-20, 20))

		weights = [0,0,0,0,0,0,0,0]
		
		weights[0] += np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[0] /= distSqr([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1])
		weights[1] += np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery + self.rect.height)], [0, 1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[1] /= distSqr([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery + self.rect.height)], [0, 1])
		weights[2] += np.dot([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery)], [-1, 0]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[2] /= distSqr([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery)], [-1, 0])
		weights[3] += np.dot([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery)], [1, 0]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[3] /= distSqr([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery)], [1, 0])
		weights[4] += np.dot([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [-1, -1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[4] /= distSqr([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [-1, -1])
		weights[5] += np.dot([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [1, -1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[5] /= distSqr([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [1, -1])
		weights[6] += np.dot([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [1, 1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[6] /= distSqr([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [1, 1])
		weights[7] += np.dot([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [-1, 1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[7] /= distSqr([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [-1, 1])

		for t in args[0]:
			if t.collidepoint((self.rect.centerx, self.rect.centery - self.rect.height)):
				weights[0] = -abs(weights[0])
			if t.collidepoint((self.rect.centerx, self.rect.centery + self.rect.height)):
				weights[1] = -abs(weights[1])
			if t.collidepoint((self.rect.centerx - self.rect.width, self.rect.centery)):
				weights[2] = -abs(weights[2])
			if t.collidepoint((self.rect.centerx + self.rect.width, self.rect.centery)):
				weights[3] = -abs(weights[3])
			if t.collidepoint((self.rect.centerx - self.rect.width, self.rect.centery - self.rect.height)):
				weights[4] = -abs(weights[4])
			if t.collidepoint((self.rect.centerx + self.rect.width, self.rect.centery - self.rect.height)):
				weights[5] = -abs(weights[5])
			if t.collidepoint((self.rect.centerx + self.rect.width, self.rect.centery + self.rect.height)):
				weights[6] = -abs(weights[6])
			if t.collidepoint((self.rect.centerx - self.rect.width, self.rect.centery + self.rect.height)):
				weights[7] = -abs(weights[7])

		weight_shaper = [1,1,1,1,1,1,1,1]
		for i in range(len(weights)):
			weights[i] *= weight_shaper[i]



		mw = float('-inf')
		mw_idx = -1
		for i in range(len(weights)):
			if weights[i] > mw:
				mw_idx = i 
				mw = weights[i]

		
		self.weights = weights

		if mw_idx == 0:
			self.moving[0] = True
		elif mw_idx == 1:
			self.moving[1] = True
		elif mw_idx == 2:
			self.moving[2] = True
		elif mw_idx == 3:
			self.moving[3] = True
		elif mw_idx == 4:
			self.moving[0] = True
			self.moving[2] = True
		elif mw_idx == 5:
			self.moving[0] = True
			self.moving[3] = True
		elif mw_idx == 6:
			self.moving[1] = True
			self.moving[3] = True
		elif mw_idx == 7:
			self.moving[1] = True
			self.moving[2] = True
		






		if dist_to_player < 40000:
			self.attack(self.player_ref.rect.center, args[2])

class Ranged_Enemy(Enemy):
	def __init__(self, pos, img = None, size = (32, 32), player_ref = None, weapon = None):
		super().__init__(pos, img, size, player_ref)
		self.speed = 1
		self.weapon = weapon
		self.weapon.owner = self

	def update(self, *args):
		super().update(args[0], args[1], args[2], args[3])

		self.image = pygame.transform.rotate(self.img, get_angle_to_pos(self.rect.topleft, self.player_ref.rect.center) + 90)

		for m in range(len(self.moving)):
			self.moving[m] = False

		dist_to_player = distSqr(self.player_ref.rect.center, self.rect.center)

		
		
		self.desired_pos = self.player_ref.rect.center
		
		weights = [0,0,0,0,0,0,0,0]
		
		weights[0] += np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[0] /= distSqr([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1])
		weights[1] += np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery + self.rect.height)], [0, 1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[1] /= distSqr([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery + self.rect.height)], [0, 1])
		weights[2] += np.dot([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery)], [-1, 0]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[2] /= distSqr([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery)], [-1, 0])
		weights[3] += np.dot([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery)], [1, 0]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[3] /= distSqr([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery)], [1, 0])
		weights[4] += np.dot([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [-1, -1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[4] /= distSqr([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [-1, -1])
		weights[5] += np.dot([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [1, -1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[5] /= distSqr([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery - self.rect.height)], [1, -1])
		weights[6] += np.dot([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [1, 1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[6] /= distSqr([self.desired_pos[0] - (self.rect.centerx + self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [1, 1])
		weights[7] += np.dot([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [-1, 1]) * abs(np.dot([self.desired_pos[0] - self.rect.centerx, self.desired_pos[1] - (self.rect.centery - self.rect.height)], [0, -1]))
		weights[7] /= distSqr([self.desired_pos[0] - (self.rect.centerx - self.rect.width), self.desired_pos[1] - (self.rect.centery + self.rect.height)], [-1, 1])

		
		for t in args[0]:
			if t.collidepoint((self.rect.centerx, self.rect.centery - self.rect.height)):
				weights[0] = -abs(weights[0])
			if t.collidepoint((self.rect.centerx, self.rect.centery + self.rect.height)):
				weights[1] = -abs(weights[1])
			if t.collidepoint((self.rect.centerx - self.rect.width, self.rect.centery)):
				weights[2] = -abs(weights[2])
			if t.collidepoint((self.rect.centerx + self.rect.width, self.rect.centery)):
				weights[3] = -abs(weights[3])
			if t.collidepoint((self.rect.centerx - self.rect.width, self.rect.centery - self.rect.height)):
				weights[4] = -abs(weights[4])
			if t.collidepoint((self.rect.centerx + self.rect.width, self.rect.centery - self.rect.height)):
				weights[5] = -abs(weights[5])
			if t.collidepoint((self.rect.centerx + self.rect.width, self.rect.centery + self.rect.height)):
				weights[6] = -abs(weights[6])
			if t.collidepoint((self.rect.centerx - self.rect.width, self.rect.centery + self.rect.height)):
				weights[7] = -abs(weights[7])

		weight_shaper = []
		
		if dist_to_player < 200 * 200:
			weight_shaper =  [-1, -1, -1, -1, -1, -1, -1, -1]
		elif dist_to_player > 400 * 400:
			weight_shaper = [1, 1, 1, 1, 1, 1, 1, 1]
		else:
			weight_shaper =  [0, 0, 0, 0, 0, 0, 0, 0]

		


		for i in range(len(weights)):
			weights[i] *= weight_shaper[i]


		mw = float('-inf')
		mw_idx = -1
		for i in range(len(weights)):
			if weights[i] > mw:
				mw_idx = i 
				mw = weights[i]

		#print(weights)

		self.weights = weights

		if mw_idx == 0:
			self.moving[0] = True
		elif mw_idx == 1:
			self.moving[1] = True
		elif mw_idx == 2:
			self.moving[2] = True
		elif mw_idx == 3:
			self.moving[3] = True
		elif mw_idx == 4:
			self.moving[0] = True
			self.moving[2] = True
		elif mw_idx == 5:
			self.moving[0] = True
			self.moving[3] = True
		elif mw_idx == 6:
			self.moving[1] = True
			self.moving[3] = True
		elif mw_idx == 7:
			self.moving[1] = True
			self.moving[2] = True
		


		if dist_to_player < 360000:
			self.attack(self.player_ref.rect.center, args[2])

class Boss(Enemy):

	AT_PLAYER = 0
	SPIRAL = 1
	ANTI_SPIRAL = 2
	TWIN_SPIRALS = 3
	CIRCLE = 4
	DOUBLE_SPIRAL = 5
	QUAD_SPIRAL = 6
	LASERS = 7

	def __init__(self, pos, img = None, size = (32, 32), player_ref = None, patterns = None, bullet_img = None):
		super().__init__(pos, img, size, player_ref)
		self.speed = 1
		self.health = 100
		self.patterns = patterns
		self.pattern = self.patterns[0]
		self.bullet_img = bullet_img
		self.time_per_pattern = 6000
		self.last_pattern_switch = 0
		self.angle_offset = 0
		self.fired_last = 0
		self.fire_cooldown = 100

	def update(self, *args):
		super().update(args[0], args[1], args[2], args[3])

		self.image = pygame.transform.rotate(self.img, get_angle_to_pos(self.rect.topleft, self.player_ref.rect.center) - 90)

		for m in range(len(self.moving)):
			self.moving[m] = False

		dist_to_player = distSqr(self.player_ref.rect.center, self.rect.center)

		if self.time_per_pattern <= pygame.time.get_ticks() - self.last_pattern_switch:
			self.pattern = random.choice(self.patterns)
			self.last_pattern_switch = pygame.time.get_ticks()
			self.angle_offset = 0

		x_dist = self.player_ref.rect.centerx - self.rect.centerx
		y_dist = -(self.player_ref.rect.centery - self.rect.centery)
		angle = math.degrees(math.atan2(y_dist, x_dist))
		angle = math.radians(angle)
		radius = 60
		if self.fire_cooldown <= pygame.time.get_ticks() - self.fired_last:
			self.fired_last = pygame.time.get_ticks()
			if self.pattern == self.AT_PLAYER:
				self.angle_offset = 0
				self.fire_cooldown = 100
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img))
			elif self.pattern == self.SPIRAL:
				self.fire_cooldown = 100
				angle = angle + self.angle_offset
				self.angle_offset += 5
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
			elif self.pattern == self.ANTI_SPIRAL:
				self.fire_cooldown = 100
				angle = angle + self.angle_offset
				self.angle_offset += 5
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
			elif self.pattern == self.TWIN_SPIRALS:
				self.fire_cooldown = 250
				angle = angle + self.angle_offset
				self.angle_offset += 5
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
				angle = angle - 2 * self.angle_offset
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
			elif self.pattern == self.CIRCLE:
				self.fire_cooldown = 3000
				start_angle = angle			
				for i in range(35):
					angle = math.radians(start_angle + i * 10)				
					bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
					args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 1))
			elif self.pattern == self.DOUBLE_SPIRAL:
				self.fire_cooldown = 250
				angle = angle + self.angle_offset
				self.angle_offset += 5
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
				angle = angle + 180
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
			elif self.pattern == self.QUAD_SPIRAL:
				self.fire_cooldown = 250
				angle = angle + self.angle_offset
				self.angle_offset += 5
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
				angle = angle + 90
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
				angle = angle + 180
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
				angle = angle + 270
				bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
				args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 2))
			elif self.pattern == self.LASERS:
				self.fire_cooldown = 250
				self.angle_offset += 10
				start_angle = angle			
				for i in range(5):
					angle = math.radians(start_angle + i * 72+ self.angle_offset)				
					bullet_start_pos = [self.rect.centerx + math.cos(angle) * radius, self.rect.centery - math.sin(angle) * radius]
					args[2].add(Projectile(bullet_start_pos, angle = angle, dist = 1000, img = self.bullet_img, speed = 1))

	def damage(self, amount):
		self.health -= amount
		if self.health <= 0:
			self.alive = False


class Projectile(Entity):
	def __init__(self, pos, img = None, size = (8, 8), angle = 0, dist = 10, speed = 8):
		rect = img.get_bounding_rect()
		surf = pygame.Surface(rect.size)
		surf.set_colorkey((0,0,0))
		surf.blit(img, (-rect.x, -rect.y))


		super().__init__(pos, surf, size)
		self.color = self.img.get_at((self.img.get_width() // 2, self.img.get_height() // 2))
		self.angle = angle
		self.speed = speed
		self.range = dist
		#TODO : fix this for some reason 500 range == 300 in game dont know why
		self.life_time = (self.range / self.speed) * 10
		#print(self.life_time)
		self.life_start = pygame.time.get_ticks()

		

	def update(self, *args):
		if self.enabled:
					if self.alive:
						self.v[0] = self.speed * math.cos(self.angle)
						self.v[1] = self.speed * -math.sin(self.angle)

						dx = self.v[0]
						dy = self.v[1]

						dx, dy = self.collide(dx, dy, args[0], args[1], args[2], args[3])

						self.pos[0] += dx
						self.pos[1] += dy

						self.rect.center = (self.pos)

					if pygame.time.get_ticks() > self.life_time + self.life_start:
						self.alive = False

	def collide(self, dx, dy, tiles, entity_list, weapon_pickups, particles):
		if False:
			for t in tiles:			
				if t.rect.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
					self.alive = False
					for i in range(10):
						offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
						particles.add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, self.color))

				if t.rect.colliderect(pygame.Rect((self.rect.x, self.rect.y + dy), self.rect.size)):
					self.alive = False
					for i in range(10):
						offset = [0, 0]
						if dx < 0:
							offset[0] = random.randrange(0, 10) - 10							
						else:
							offset[0] = random.randrange(-20, 0) - 10
							

						if dy < 0:
							offset[1] = random.randrange(0, 10) - 10
							particles.add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, self.color))
						else:
							offset[1] = random.randrange(-20, 0) - 10
							particles.add(Particles([self.rect.bottomleft[0] + offset[0], self.rect.bottomleft[1] + offset[1]], [0,0], [0,0], 500, self.color))
		loc_str = str(int((self.pos[0] + dx) //	64)) + ';' + str(int((self.pos[1] + dy) // 64))
		#print(loc_str)
		#print(tiles)

		if loc_str in tiles:
			if tiles[loc_str] == 4 or tiles[loc_str] == 5:
				self.alive = False
				for i in range(10):
					offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
					particles.add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, self.color))
		for e in entity_list:
			if e != self:
				if e.rect.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
					e.collide_with(self, entity_list, particles)
					self.alive = False
					
				if e.rect.colliderect(pygame.Rect((self.rect.x, self.rect.y + dy), self.rect.size)):
					e.collide_with(self, entity_list, particles)
					self.alive = False
		
		for wp in weapon_pickups:
			if wp.rect.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
					wp.collide_with(self, entity_list, particles, weapon_pickups)
					
			if wp.rect.colliderect(pygame.Rect((self.rect.x, self.rect.y + dy), self.rect.size)):
				wp.collide_with(self, entity_list, particles, weapon_pickups)

		
		return dx, dy


class Weapon():
	def __init__(self, damage, weapon_range = None, owner = None, projectiles_per_attack = 1, cooldown = 300, bullet_img = None, img = None, mana_cost = 1):
		self.damage = damage
		self.range = weapon_range
		self.projectiles_per_attack = projectiles_per_attack
		self.cooldown = cooldown #in miliseconds
		self.fired_last = 0
		self.owner = owner
		self.bullet_img = bullet_img
		self.img = img
		self.angle = 0
		self.mana_cost = mana_cost

	def attack(self, pos, projectiles, angle):
		
		for i in range(self.projectiles_per_attack):
			
			x_dist = pos[0] - self.owner.pos[0]
			y_dist = -(pos[1] - self.owner.pos[1])

			#offset by x degrees per projectile per attack
			if self.projectiles_per_attack > 1:
				offset = 45 
				iterator = i * offset * 2 / (self.projectiles_per_attack - 1)
				
				self.angle = math.degrees(math.atan2(y_dist, x_dist)) - offset + iterator
			else:
				self.angle = math.degrees(math.atan2(y_dist, x_dist))
			self.angle = math.radians(self.angle)
			radius = 60
			bullet_start_pos = [self.owner.rect.centerx + math.cos(self.angle) * radius, self.owner.rect.centery - math.sin(self.angle) * radius]
			projectiles.add(Projectile(bullet_start_pos, angle = self.angle, dist = self.range, img = self.bullet_img))
			self.fired_last = pygame.time.get_ticks()

	def drop(self, pickup_list):
		self.angle = math.radians(math.degrees(self.angle) - 45 + 180)
		pickup_list.add(WeaponPickup([self.owner.rect.center[0] + math.cos(self.angle) * 100, self.owner.rect.center[1] - math.sin(self.angle) * 100], self.img, self.img.get_size(),
		 Weapon(self.damage, self.range, None, self.projectiles_per_attack, self.cooldown, self.bullet_img, self.img, self.mana_cost)))



#class Item():
#	def __init__(self, img, )



class DoorWay(pygame.sprite.Sprite):
	def __init__(self, pos, img, size):
		pygame.sprite.Sprite.__init__(self)
		self.pos = pos 
		self.image = pygame.transform.scale(img, (size)) 
		self.size = size
		self.rect = pygame.Rect(self.pos, self.size)
		self.enabled = True

	def update(self, *args):
		if self.enabled:
			self.collide(args[0], args[1])

	def collide(self, player, game_manager):
		if player.rect.colliderect(pygame.Rect(self.pos, self.size)):
			self.enabled = False
			player.dungeon_transition = True
			
			
		if player.rect.colliderect(pygame.Rect(self.pos, self.size)):
			self.enabled = False
			player.dungeon_transition = True


class Health_Chest(pygame.sprite.Sprite):
	def __init__(self, pos, img_closed, img_open, size, health_img):
		pygame.sprite.Sprite.__init__(self)
		self.pos = pos 
		self.image = pygame.transform.scale(img_closed, (size)) 
		self.image_open = pygame.transform.scale(img_open, (size)) 
		self.health_img = health_img
		self.size = size
		self.rect = pygame.Rect(self.pos, self.size)
		self.enabled = True
		self.opened = False

	def update(self, *args):
		if self.enabled:
			self.collide(args[0], args[1])

	def open(self, pickup_list):
		pickup_list.add(HealthPickup([self.rect.x, self.rect.y], self.health_img, self.health_img.get_size()))
		self.enabled = False

	def collide(self, player, pickup_list):
		if self.enabled:
			if player.rect.colliderect(pygame.Rect(self.pos, self.size)):
				if not self.opened:			
					self.image = self.image_open
					self.open(pickup_list)
					self.opened = True
				
class Weapons_Chest(pygame.sprite.Sprite):
	def __init__(self, pos, img_closed, img_open, size, weapon_imgs, bullet_imgs):
		pygame.sprite.Sprite.__init__(self)
		self.pos = pos 
		self.image = pygame.transform.scale(img_closed, (size)) 
		self.image_open = pygame.transform.scale(img_open, (size)) 
		self.weapon_imgs = weapon_imgs
		self.bullet_imgs = bullet_imgs
		self.size = size
		self.rect = pygame.Rect(self.pos, self.size)
		self.enabled = True
		self.opened = False

	def update(self, *args):
		if self.enabled:
			self.collide(args[0], args[1])

	def open(self, pickup_list):
		img = random.choice(self.weapon_imgs)
		bullet_img = random.choice(self.bullet_imgs)
		damage = random.randrange(1, 3)
		weapon_range = random.randrange(250, 1000)
		num_projectiles = random.randrange(1, 11)
		weapon_cooldown = random.randrange(100, 1000)
		mana_cost = max(int(damage / 3 + weapon_range / 1000 + num_projectiles / 11 + weapon_cooldown / 1000), 1)
		#print(damage, weapon_range, num_projectiles, weapon_cooldown, mana_cost)
		pickup_list.add(WeaponPickup([self.rect.x, self.rect.y], img, img.get_size(),
	 Weapon(damage, weapon_range, None, num_projectiles, weapon_cooldown, bullet_img, img, mana_cost)))
		self.enabled = False

	def collide(self, player, pickup_list):
		if self.enabled:
			if player.rect.colliderect(pygame.Rect(self.pos, self.size)):
				if not self.opened:			
					self.image = self.image_open
					self.open(pickup_list)
					self.opened = True
				
			


class PickUp(pygame.sprite.Sprite):
	def __init__(self, pos, img, size):
		pygame.sprite.Sprite.__init__(self)
		self.pos = pos 
		self.image = pygame.transform.scale(img, (size)) 
		self.size = size
		self.rect = pygame.Rect([self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2], self.size)
		self.enabled = True
		self.name = 'Pickup'
		self.text = 'A Pickup'

	def update(self, *args):
		if self.enabled:
			self.collide(args[0], args[1], args[2], args[3])

	def collide(self, entity_list, projectiles, particles, weapon_pickups):
		for e in entity_list:
			if e != self:
				if e.rect.colliderect(pygame.Rect(self.pos, self.size)):
					self.collide_with(e, entity_list, particles, weapon_pickups)
					
				if e.rect.colliderect(pygame.Rect(self.pos, self.size)):
					self.collide_with(e, entity_list, particles, weapon_pickups)

class HealthPickup(PickUp):
	def __init__(self, pos, img, size):
		super().__init__(pos, img, size)
		self.heal_amount = random.randrange(5, 10)
		self.name = 'Health Pack'
		self.text = f'Heal for :{self.heal_amount}'


	def update(self, *args):

		super().update(args[0], args[1], args[2], args[3])

	def collide_with(self, *args):
		if self.enabled:
			if isinstance(args[0], Projectile):			
				for i in range(10):
					offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
					args[2].add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (255, 255, 0)))
				self.enabled = False
				self.kill()
			elif isinstance(args[0], Entity):
				
				args[0].heal(self.heal_amount)
				self.enabled = False
				self.kill()



class WeaponPickup(PickUp):

	def __init__(self, pos, img, size, weapon):
		super().__init__(pos, img, size)
		self.weapon = weapon
		self.name = 'Weapon Pickup'
		self.text = f'D : {self.weapon.damage} P : {self.weapon.projectiles_per_attack}, R : {self.weapon.range} CD : {self.weapon.cooldown}, MC : {self.weapon.mana_cost}'
		
	def update(self, *args):

		super().update(args[0], args[1], args[2], args[3])

	def collide_with(self, *args):
		if self.enabled:
			if isinstance(args[0], Projectile):			
				for i in range(10):
					offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
					args[2].add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (255, 255, 0)))
				self.kill()
				self.enabled = False
			elif isinstance(args[0], Entity):				
				args[0].pickup(self.weapon, args[3])
				self.enabled = False
				self.kill()



class Particles(pygame.sprite.Sprite):

	def __init__(self, pos, v, a, life_span, color = (200, 200, 200), starting_radius = 24):
		pygame.sprite.Sprite.__init__(self)
		self.pos = pos
		self.v = v 
		self.a = a 
		self.life_time = 0
		self.life_span = life_span
		self.life_start = pygame.time.get_ticks()
		
		size = (24, 24)
		image = pygame.Surface(size)
		self.image = image
		self.color = color
		self.radius = starting_radius
		self.rect = pygame.Rect(self.pos, size)

	def update(self):
		if self.life_span + self.life_start >= pygame.time.get_ticks():
			self.life_time = self.life_span - (pygame.time.get_ticks() - self.life_start)
			size = (self.life_time / self.life_span * self.radius, self.life_time / self.life_span * self.radius)
			image = pygame.Surface(size)
			image.fill((100, 100, 100))
			temp_image = pygame.Surface(size)
			pygame.draw.circle(temp_image, self.color, (size[0] // 2, size[1] // 2), size[0] // 2)
			image.set_colorkey((0,0,0))
			image.blit(temp_image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
			self.image = image

			self.v[0] += self.a[0]
			self.v[1] += self.a[1]

			self.pos[0] += self.v[0]
			self.pos[1] += self.v[1]
			self.rect = pygame.Rect(self.pos, size)
		else:
			self.kill()


		

