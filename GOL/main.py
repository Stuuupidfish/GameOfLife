#importing libraries
import pygame, sys, copy, asyncio

#i gotta run this in 3.13 so this is a note to myself:
# py -3.13 GameOfLife.py

#initialize Pygame
pygame.init()

#set dimensions and scale
BLOCK_WIDTH = 20
GRID_WIDTH = 40
GRID_HEIGHT = 30
UI_HEIGHT = 50

#create screen & clock
screen = pygame.display.set_mode((GRID_WIDTH * BLOCK_WIDTH, GRID_HEIGHT * BLOCK_WIDTH + UI_HEIGHT))
clock = pygame.time.Clock()

#make a grid to store RGB values
def initGrid():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
grid = initGrid()

#create lines to outline the grid
#pygame.draw.line(surface, color, start_pos, end_pos, width=1)
def drawGridLines():
    for i in range(GRID_WIDTH):
        pygame.draw.line(screen, (30, 30, 30), (BLOCK_WIDTH*i, 0), (BLOCK_WIDTH*i, GRID_HEIGHT*BLOCK_WIDTH))
    for j in range(GRID_HEIGHT):
        pygame.draw.line(screen, (30, 30, 30), (0, BLOCK_WIDTH*j), (GRID_WIDTH*BLOCK_WIDTH, BLOCK_WIDTH*j))

generation = 0 
population = 0

def updateGrid():
    global grid, generation
    generation += 1
    duplicate = copy.deepcopy(grid)
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            neighbors = numLiveNeighbor(grid, r, c)
            if grid[r][c] == 1:
                if neighbors < 2:
                    duplicate[r][c] = 0
                if neighbors > 3:
                    duplicate[r][c] = 0
            else:
                if neighbors == 3:
                    duplicate[r][c] = 1
    grid = duplicate

def numLiveNeighbor(board, r, c):
    count = 0
    if r - 1 >= 0 and c - 1 >= 0 and board[r - 1][c - 1] == 1:
        # top left
        count += 1
    if r - 1 >= 0 and board[r - 1][c] == 1:
        # top middle
        count += 1
    if r - 1 >= 0 and c + 1 < len(board[0]) and board[r - 1][c + 1] == 1:
        # top right
        count += 1
    if c - 1 >= 0 and board[r][c - 1] == 1:
        # middle left
        count += 1
    if c + 1 < len(board[0]) and board[r][c + 1] == 1:
        # middle right
        count += 1
    if r + 1 < len(board) and c - 1 >= 0 and board[r + 1][c - 1] == 1:
        # bottom left
        count += 1
    if r + 1 < len(board) and board[r + 1][c] == 1:
        # bottom middle
        count += 1
    if r + 1 < len(board) and c + 1 < len(board[0]) and board[r + 1][c + 1] == 1:
        # bottom right
        count += 1
    return count


cells = {}

speeds = [0.25, 0.5, 1, 2] #updates per second

curSpeed = 0; #index for speeds list

# Timer for grid updates
updateTimer = 0.0
updateInterval = 1.0 / speeds[curSpeed]  # seconds between updates

pause = False

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        textSurf = self.font.render(self.text, True, (0, 0, 0))
        textRect = textSurf.get_rect(center=self.rect.center)
        surface.blit(textSurf, textRect)

    def isClicked(self, pos):
        return self.rect.collidepoint(pos)

speedButton = Button(10, GRID_HEIGHT * BLOCK_WIDTH + 10, 80, 30, "Speed")
pauseButton = Button(100, GRID_HEIGHT * BLOCK_WIDTH + 10, 80, 30, "Pause")

font = pygame.font.Font(None, 32) 

async def main():
    global updateTimer, updateInterval, running, pauseButton, curSpeed, speedButton, pause
    #while the program is running-- continuously updates
    running = True
    while running: #aka run == True
        dt = clock.tick(60) / 1000.0  # Run at 60 FPS, get delta time in seconds
        if not pause:
            updateTimer += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  #left mouse button
                    x, y = pygame.mouse.get_pos()
                    if y < GRID_HEIGHT * BLOCK_WIDTH: 
                        gridX = x // BLOCK_WIDTH  # Calculate which column in the grid
                        gridY = y // BLOCK_WIDTH  # Calculate which row in the grid
                        #update the color of the clicked square
                        state = grid[gridY][gridX];
                        if state == 0:
                            grid[gridY][gridX] = 1
                            cells[(gridX, gridY)] = True  # Add to live cells list
                        else:
                            grid[gridY][gridX] = 0
                            cells.pop((gridX, gridY))  # Remove from live cells list
                if speedButton.isClicked(event.pos):
                    curSpeed = (curSpeed + 1) % len(speeds)  # Cycle through speeds
                    updateInterval = 1.0 / speeds[curSpeed]  # Update interval based on new speed
                if pauseButton.isClicked(event.pos):
                    pause = not pause
                    pauseButton.text = "Resume" if pause else "Pause"

        

        #refreshes screen
        screen.fill((0, 0, 0))
        population = 0
        for row in range(GRID_HEIGHT):
            for column in range(GRID_WIDTH):
                color = grid[row][column]
                if color != 0:  # Only draw if the cell is not empty
                    pygame.draw.rect(screen, (255,255,255), pygame.Rect(column * BLOCK_WIDTH, row * BLOCK_WIDTH, BLOCK_WIDTH, BLOCK_WIDTH))
                    population += 1
                else:
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(column * BLOCK_WIDTH, row * BLOCK_WIDTH, BLOCK_WIDTH, BLOCK_WIDTH))
                    #population += 0
        drawGridLines()
        speedButton.draw(screen)
        pauseButton.draw(screen)
        speedText = font.render(f"Speed: {speeds[curSpeed]}x", True, (255, 255, 255))
        generationText = font.render(f"Generation: {generation}", True, (255, 255, 255))
        populationText = font.render(f"Population: {population}", True, (255, 255, 255))
        screen.blit(speedText, (200, GRID_HEIGHT * BLOCK_WIDTH + 15))
        screen.blit(generationText, (350, GRID_HEIGHT * BLOCK_WIDTH + 15))
        screen.blit(populationText, (550, GRID_HEIGHT * BLOCK_WIDTH + 15))
        pygame.display.update()
        
        # Update grid only when enough time has passed
        if updateTimer >= updateInterval:
            updateGrid()
            updateTimer = 0.0
            # Recalculate interval if speed changed
            updateInterval = 1.0 / speeds[curSpeed]
        
        await asyncio.sleep(0)

    #quits the program
    #pygame.quit()

asyncio.run(main())
# sys.exit()
