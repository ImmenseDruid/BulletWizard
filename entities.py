import pygame, math, random

def distSqr(p1, p2):
	return ((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))

def get_angle_to_pos(startpos, endpos):
	x_dist = startpos[0] - endpos[0]
	y_dist = -(startpos[1] - endpos[1])
	return math.degrees(math.atan2(y_dist, x_dist))

class Camera():
	def __init__(self, size):
		self.pos = [0,0]
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
	


class Static_Entity(pygame.sprite.Sprite):
	def __init__(self, pos, img = None, size = (32, 32)):
		pygame.sprite.Sprite.__init__(self)

		if not img:
			img = pygame.Surface(size)
			pygame.draw.rect(img, (0, 0, 255), ((0,0), size))

		img = pygame.transform.scale(img, size)

		self.pos = pos
		self.image = img
		self.size = size
		self.rect = pygame.Rect(pos, self.size)
		self.enabled = True

	def collide(self, entity):
		pass


	def draw(self, screen, camera):
		screen.blit(self.image, (self.rect.x - camera.pos[0], self.rect.y - camera.pos[1]))

class Wall(Static_Entity):
	def __init__(self, pos, img = None, size = (32, 32)):
		super().__init__(pos, img, size)

	def collide(self, entity):
		super().collide(entity)
		

class Spiked_Wall(Static_Entity):
	def __init__(self, pos, img = None, size = (32, 32)):
		super().__init__(pos, img, size)

	def collide(self, entity):
		super().collide(entity)
		entity.damage(1)

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

		self.dash_cooldown = 2000
		self.last_dash = -2000

	def update(self, *args):
		if self.enabled:
			if self.alive:
				self.v[0] += self.a[0]
				self.v[1] += self.a[1]

				dx = self.v[0]
				dy = self.v[1]

				dx, dy = self.collide(dx, dy, args[0], args[1], args[3])

				self.pos[0] += dx
				self.pos[1] += dy

				self.rect.center = self.pos
				#self.rect.y = self.pos[1]

	def collide(self, dx, dy, tiles, entity_list, particles):
	
		for t in tiles:
			if t.rect.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
				t.collide(self)
				if self.v[0] < 0:
					dx = t.rect.x + t.rect.w - self.rect.x
				elif self.v[0] > 0:
					dx = t.rect.x - self.rect.w - self.rect.x

				self.v[0] = 0
			if t.rect.colliderect(pygame.Rect((self.rect.x, self.rect.y + dy), self.rect.size)):
				t.collide(self)
				if self.v[1] < 0:
					dy = t.rect.y + t.rect.h - self.rect.y
				elif self.v[1] > 0:
					dy = t.rect.y - self.rect.h - self.rect.y

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
		print(type(args[0]))

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

		elif isinstance(args[0], WeaponPickup): 
			self.drop(args[1])
			self.weapon = args[0].weapon
			self.weapon.owner = self
			for i in range(10):
				offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
				args[2].add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (255, 255, 255)))
			args[0].kill()
			#del args[0]
			


	def damage(self, amount):
		self.health -= amount
		if self.health <= 0:
			
			self.alive = False

	def attack(self, pos, projectiles):
		if self.alive and self.enabled:
			if self.weapon:			
				if pygame.time.get_ticks() >= self.weapon.fired_last + self.weapon.cooldown:
					x_dist = pos[0] - self.rect.center[0]
					y_dist = -(pos[1] - self.rect.center[1])
					angle = math.degrees(math.atan2(y_dist, x_dist))
					force_angle = math.radians(math.degrees(math.atan2(y_dist, x_dist)) + 180)

					force = 2

					self.v[0] += math.cos(force_angle) * force
					self.v[1] += -math.sin(force_angle) * force
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


	def drop(self, entity_list):
		if self.weapon is not None:
			self.weapon.drop(entity_list)
			self.weapon = None

	def draw(self, screen):
		screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(Entity):
	def __init__(self, pos, img = None, size = (32, 32)):
		if not img:
			img = pygame.Surface(size)
			pygame.draw.rect(img, (255, 255, 255), ((0,0), size))
		super().__init__(pos, img, size)
		

		self.speed = 2
		

	def update(self, *args):	

		self.image = pygame.transform.rotate(self.img, get_angle_to_pos(self.rect.topleft, args[4]) + 90)

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

class Enemy(Entity):
	def __init__(self, pos, img = None, size = (32, 32), player_ref = None):
		if not img:
			img = pygame.Surface(size)
			pygame.draw.rect(img, (255, 0, 0), ((0,0), size))

		self.speed = 1
		self.player_ref = player_ref
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
	def __init__(self, pos, img = None, size = (32, 32), player_ref = None):
		super().__init__(pos, img, size, player_ref)


	def update(self, *args):
		super().update(args[0], args[1], args[2], args[3])

		self.image = pygame.transform.rotate(self.img, get_angle_to_pos(self.rect.topleft, self.player_ref.rect.center) + 90)

		for m in range(len(self.moving)):
			self.moving[m] = False

		dist_to_player = distSqr(self.player_ref.rect.center, self.rect.center)

		if dist_to_player < 250000 and dist_to_player > 10000:
			if self.player_ref.rect.center[0] > self.rect.center[0] + 100:
				self.moving[3] = True
				
			elif self.player_ref.rect.center[0] < self.rect.center[0] - 100:
				self.moving[2] = True

			if self.player_ref.rect.center[1] > self.rect.center[1] + 100:
				self.moving[1] = True
				
			elif self.player_ref.rect.center[1] < self.rect.center[1] - 100:
				self.moving[0] = True


		if dist_to_player < 40000:
			self.attack(self.player_ref.rect.center, args[2])

class Ranged_Enemy(Enemy):
	def __init__(self, pos, img = None, size = (32, 32), player_ref = None):
		super().__init__(pos, img, size, player_ref)
		self.speed = 1

	def update(self, *args):
		super().update(args[0], args[1], args[2], args[3])

		self.image = pygame.transform.rotate(self.img, get_angle_to_pos(self.rect.topleft, self.player_ref.rect.center) + 90)

		for m in range(len(self.moving)):
			self.moving[m] = False

		dist_to_player = distSqr(self.player_ref.rect.center, self.rect.center)

		if dist_to_player < 40000:
			#print(dist_to_player)
			if self.player_ref.rect.center[0] > self.rect.center[0]:
				self.moving[2] = True
				
			elif self.player_ref.rect.center[0] < self.rect.center[0]:
				self.moving[3] = True

			if self.player_ref.rect.center[1] > self.rect.center[1]:
				self.moving[0] = True
				
			elif self.player_ref.rect.center[1] < self.rect.center[1]:
				self.moving[1] = True


		if dist_to_player < 360000:
			self.attack(self.player_ref.rect.center, args[2])


class Projectile(Entity):
	def __init__(self, pos, img = None, size = (8, 8), angle = 0, dist = 10):
		super().__init__(pos, img, size)

		self.angle = angle
		self.speed = 8
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

						dx, dy = self.collide(dx, dy, args[0], args[1], args[2])

						self.pos[0] += dx
						self.pos[1] += dy

						self.rect.center = (self.pos)

					if pygame.time.get_ticks() > self.life_time + self.life_start:
						self.alive = False

	def collide(self, dx, dy, tiles, entity_list, particles):
		if False:
			for t in tiles:			
				if t.rect.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
					self.alive = False
					for i in range(10):
						offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
						particles.add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (0, 0, 255)))

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
							particles.add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (0, 0, 255)))
						else:
							offset[1] = random.randrange(-20, 0) - 10
							particles.add(Particles([self.rect.bottomleft[0] + offset[0], self.rect.bottomleft[1] + offset[1]], [0,0], [0,0], 500, (0, 0, 255)))
				
		for e in entity_list:
			if e != self:
				if e.rect.colliderect(pygame.Rect((self.rect.x + dx, self.rect.y), self.rect.size)):
					e.collide_with(self, entity_list, particles)
					
				if e.rect.colliderect(pygame.Rect((self.rect.x, self.rect.y + dy), self.rect.size)):
					e.collide_with(self, entity_list, particles)
					
		
		return dx, dy


class Weapon():
	def __init__(self, damage, weapon_range = None, owner = None, projectiles_per_attack = 1, cooldown = 300, bullet_img = None, img = None):
		self.damage = damage
		self.range = weapon_range
		self.projectiles_per_attack = projectiles_per_attack
		self.cooldown = cooldown #in miliseconds
		self.fired_last = 0
		self.owner = owner
		self.bullet_img = bullet_img
		self.img = img
		self.angle = 0 

	def attack(self, pos, projectiles, angle):
		
		for i in range(self.projectiles_per_attack):
			
			x_dist = pos[0] - self.owner.rect.topleft[0]
			y_dist = -(pos[1] - self.owner.rect.topleft[1])

			#offset by x degrees per projectile per attack
			if self.projectiles_per_attack > 1:
				offset = 45 
				iterator = i * offset * 2 / (self.projectiles_per_attack - 1)
				
				self.angle = math.degrees(math.atan2(y_dist, x_dist)) - offset + iterator
			else:
				self.angle = math.degrees(math.atan2(y_dist, x_dist))
			self.angle = math.radians(self.angle)
			radius = 60
			bullet_start_pos = [self.owner.rect.x + math.cos(self.angle) * radius, self.owner.rect.y - math.sin(self.angle) * radius]
			projectiles.add(Projectile(bullet_start_pos, angle = self.angle, dist = self.range, img = self.bullet_img))
			self.fired_last = pygame.time.get_ticks()

	def drop(self, entity_list):
		self.angle = math.radians(math.degrees(self.angle) - 45 + 180)
		entity_list.add(WeaponPickup([self.owner.rect.center[0] + math.cos(self.angle) * 100, self.owner.rect.center[1] - math.sin(self.angle) * 100], self.img, self.img.get_size(),
		 Weapon(self.damage, self.range, None, self.projectiles_per_attack, self.cooldown, self.bullet_img, self.img)))

class WeaponPickup(Entity):

	def __init__(self, pos, img, size, weapon):
		super().__init__(pos, img, size)
		self.weapon = weapon

	def update(self, *args):
		super().update(args[0], args[1], args[2], args[3])

	def collide_with(self, *args):
		if isinstance(args[0], Projectile):
			
			for i in range(10):
				offset = [random.randrange(-20, 20), random.randrange(-20, 20)]
				args[2].add(Particles([self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]], [0,0], [0,0], 500, (255, 255, 0)))
			self.kill()
			del self



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


		

