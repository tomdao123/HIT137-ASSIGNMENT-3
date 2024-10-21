import pygame 

class Button():
	def __init__(self,x, y, image, scale):
		"""Initializes the button with position, image, and scale"""
		#the button image scale
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		#setting the button's rectangle for positioning
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		#tracking if the button has been clicked
		self.clicked = False

	def draw(self, surface):
		"""draws the button on the given surface and check for interactions"""
		action = False

		#getting the mouse position
		pos = pygame.mouse.get_pos()

		#checking mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True #button was clicked
				self.clicked = True #prevents multiple clicks

		#resets the clicked state when the mouse button is released
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draws the button on the surface
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action #returns whether the button was clicked

	def isOver(self, pos):
		"""checks if the mouse position is over the button."""
		if pos[0] > self.rect.x and pos[0] < self.rect.x + self.rect.width:
			if pos[1] > self.rect.y and pos[1] < self.rect.y + self.rect.height:
				return True
		return False