# This program generates a partial tessellation of hexagons which have randomly
# generated images embedded within them. The points are calculated pseudo-randomly,
# with simple rules (also randomly determined) dictating where the points are allowed
# to land. The general process is this:
#   1. Pick a random point within the shape
#   2. Pick a random vertex of the shape
#   3. Draw a line between the two points
#   4. Go part of the way along this line (one half, one third, one quarter, etc.)
#       (this part is also randomly determined)
#   5. The new point is now the next starting point, and the process repeats
# Though this is all random, a few simple restrictions on the randomness create
# amazing patters.
#
# Rules:
#   0. The chosen vertex cannot be the previously chosen vertex
#   1. The chosen vertex cannot be one place counter-clockwise of the previous vertex
#   2. The chosen vertex cannot be two places counter-clockwise of the previous vertex
#   3. The chosen vertex cannot be three places counter-clockwise of the previous vertex
#   4. Allows midpoints of a side to be chosen

# Getting all the libraries in order to make the code run
import sys, pygame, os
import ctypes
import math, random
from colour import Color
import datetime

# Don't worry about this
pygame.init()
sys_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
current_path = os.path.dirname(__file__)
resource_path = os.path.join(current_path, 'exports')
image_path = os.path.join(resource_path, sys_time)
os.mkdir(image_path)

# If running this program from the command line, a single argument passed will become
# the seed for the random number generator. This way results are repeatable with the
# same seed.
args = sys.argv
if len(args) == 2:
	random.seed(args[1])

# Dictating size
user32 = ctypes.windll.user32
size = width, height = user32.GetSystemMetrics(0) - 100, user32.GetSystemMetrics(1) - 100
# ------------------------------------------------------------------------------

# Storing Red, Green, Blue values of different colors
black = 0, 0, 0
white = 255, 255, 255
grey = 100, 100, 100
light_blue = 100, 100, 255
dark_grey = 50, 50, 50
colors = (
Color("red"),
Color("orange"),
Color("yellow"),
Color("green"),
Color("blue"),
Color("purple")
)
#-------------------------------------------------------------------------------

# Setting up the window
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Emergence")
#-------------------------------------------------------------------------------

# The angles of a hexagon's vertices (in radians)
angles = [math.pi/6, math.pi/2, 5*math.pi/6, 7*math.pi/6, 3*math.pi/2, 11*math.pi/6]
# The possible jump factors
factors = [3/2, (1 + 5 ** 0.5) / 2, 2, math.e, 3, math.pi, 4, 5]
# The place where the coordinates of each surface are stored, with an initial one in the center of the screen
numRules = 5
coords = [(width/2 - 400, height/2 - 400)]
#-------------------------------------------------------------------------------

# This defines the framework of a hexagon
class Hex:
	r = 100
	d = 2.5*r
	def __init__(self, x, y, rules, factor):
		self.x = x
		self.y = y
		self.verts = []
		self.polyverts = []
		self.itr = 5000
		self.currentPoint = (0, 0)
		self.points = [(0, 0), (0, 0)]
		self.pointIndex = 0
		self.rules = rules
		self.factor = factor
		self.surface = pygame.Surface((4*self.r, 4*self.r))
		self.surface.set_colorkey((0, 0, 0))

		# Sets up the outside Hex
		for i in range(6):
			pnt = (
				self.r + 50 + (self.r + 50)*math.cos((math.pi/3)*i),
				self.r + 50 + (self.r + 50)*math.sin((math.pi/3)*i)
			)
			self.verts.append(pnt)

		poly = random.randint(3, 8)
		for i in range(poly):
			pnt = (
				self.r + 50 + self.r*math.cos(2*math.pi/poly*i),
				self.r + 50 + self.r*math.sin(2*math.pi/poly*i)
			)
			self.polyverts.append(pnt)

		pygame.draw.polygon(self.surface, (100, 100, 100), self.verts)
		pygame.draw.polygon(self.surface, (50, 50, 50), self.polyverts)

		self.override = len(self.polyverts) == 3
		self.prevChoice = 0

		self.grad = genGradient()

		self.genPoints()

	# Generates the 10,000 points
	def genPoints(self):
		for i in range(self.itr):
			newVert = chooseNext(self.polyverts, self.prevChoice, self.rules, self.override)
			pnt = jumppoint((self.polyverts[newVert][0], self.polyverts[newVert][1]), self.currentPoint, self.factor, self.override)
			self.points.append(pnt)
			self.currentPoint = pnt
			self.prevChoice = newVert

	def drawNext(self, surface):
		i = self.points[self.pointIndex]
		index = random.choice([0, 1])
		pygame.draw.circle(
			surface,
			(
				self.grad[int(i[index]) % 255].red*255,
				self.grad[int(i[index]) % 255].green*255,
				self.grad[int(i[index]) % 255].blue*255
			),
			i,
			1
		)
		self.pointIndex += 1

#-------------------------------------------------------------------------------
# This function defines the color gradient for every point
def genGradient():
	grad = list(colors[random.randint(0, len(colors) - 1)].range_to(colors[random.randint(0, len(colors) - 1)], 255))
	return grad
#-------------------------------------------------------------------------------
# A small mathematical function that figures out the next point in the set
def jumppoint(point1, point2, factor, override=False):
	if override:
		factor = 2
	return (point1[0] + (point2[0] - point1[0])/factor, point1[1] + (point2[1] - point1[1])/factor)
#-------------------------------------------------------------------------------

# This checks the new points that are generated against the rules
def chooseNext(points, prevChoice, rules, override=False):
	if prevChoice >= len(points):
		raise Exception("prevChoice out of range")

	fail = False
	pointIndex = random.randint(0, len(points) - 1)

	if not override:
		if rules[0]:
			while pointIndex == prevChoice:
				pointIndex = random.randint(0, len(points) - 1)
		if rules[1]:
			while pointIndex == (prevChoice % len(points)) + 1:
				pointIndex = random.randint(0, len(points) - 1)
		if rules[2]:
			while pointIndex == (prevChoice % len(points)) + 2:
				pointIndex = random.randint(0, len(points) - 1)
		if rules[3]:
			while pointIndex == (prevChoice % len(points)) + 3:
				pointIndex = random.randint(0, len(points) - 1)

	return pointIndex
#-------------------------------------------------------------------------------

# Generates True or False randomly
def randBool():
	return random.random() > 0.5
#-------------------------------------------------------------------------------
# This generates each hexagon next to each other at random angles, but always so
# that they tile on the plane
def chooseNextSpot(prevCoords):
	randAngle = random.choice(angles)
	newCoords = (prevCoords[0] + Hex.d*math.cos(randAngle), prevCoords[1] + Hex.d*math.sin(randAngle))
	return intTuple(newCoords)

#-------------------------------------------------------------------------------
def intTuple(tup):
	return (int(tup[0]), int(tup[1]))

# Generates between seven and fifteen additional hexagons
for i in range(random.randint(7, 15)):
	coord = chooseNextSpot(coords[-1])
	sorta = lambda l, r: (abs(l[0] - r[0]) < 10) and (abs(l[1] - r[1]) < 10)
	#kinda = lambda point: point[0] < 0 or point[1] < 0 or point[0] > width or point[1] > height
	while True:
		found = False
		for c in coords:
			if sorta(c, coord):
				found = True
				break
		if found:
			coord = chooseNextSpot(coords[-1])
		else:
			break

	coords.append(coord)
	if coord[0] > width or coord[0] < 0 or coord[1] > height or coord[1] < 0:
		break

# The loop that is called every iteration
hexes = [Hex(j[0], j[1], [randBool() for i in range(numRules)], random.choice(factors)) for j in coords]
currentHex = 0
dots_per_poly = 5000
itrs_left = dots_per_poly
dots_per_itr = 1000
screen.fill((255, 255, 255))
walk_speed = 2
xshift = 0
yshift = 0
images = 1
while currentHex < len(hexes):
	# Turns off the program if someone presses the red X
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()

	if itrs_left > 0:
		for i in range(dots_per_itr):
			hexes[currentHex].drawNext(hexes[currentHex].surface)
			screen.blit(hexes[currentHex].surface, coords[currentHex])
		pygame.display.flip()
		itrs_left -= dots_per_itr
		pygame.image.save(screen, os.path.join(image_path, f"{images}.png"))
		images += 1
	else:
		currentHex += 1
		itrs_left = dots_per_poly

	for hex in hexes[:currentHex]:
		screen.blit(hex.surface, (hex.x, hex.y))
		pygame.display.flip()


	# Draws each hexagon on the window

	# The library is double-buffered, meaning nothing is shown until this function
	# is called. This way, everything is smooth and the animation is totally complete
	# when the image is eventually drawn

# Stores how the coordinates have shifted so the arrow keys can move the shape
while True:
	# Senses keys
	keys = pygame.key.get_pressed()

	# Does stuff with the arrow keys
	if keys[pygame.K_UP]:
		yshift += walk_speed
	if keys[pygame.K_DOWN]:
		yshift -= walk_speed
	if keys[pygame.K_LEFT]:
		xshift += walk_speed
	if keys[pygame.K_RIGHT]:
		xshift -= walk_speed
	if keys[pygame.K_SPACE]:
		Hex.r *= 2
		Hex.d *= 2
		screen.fill(white)
		walk_speed *= 2
		for hex in hexes:
			hex.x *= 2
			hex.y *= 2
			hex.surface = pygame.transform.scale(hex.surface, (4*Hex.r, 4*Hex.r))
	if keys[pygame.K_0]:
		Hex.r *= 0.5
		Hex.d *= 0.5
		screen.fill(white)
		walk_speed *= 0.5
		for hex in hexes:
			hex.x *= 0.5
			hex.y *= 0.5
			hex.surface = pygame.transform.scale(hex.surface, (int(0.5*Hex.r), int(0.5*Hex.r)))
	# Draws the background
	screen.fill(white)

	# Draws each hexagon on the window
	for i in hexes:
		screen.blit(i.surface, (i.x + xshift, i.y + yshift))

	# The library is double-buffered, meaning nothing is shown until this function
	# is called. This way, everything is smooth and the animation is totally complete
	# when the image is eventually drawn
	pygame.display.flip()

	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
