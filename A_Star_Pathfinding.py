import random, pygame, sys, math
from pygame import gfxdraw

# Setting the Recursion Limit-------------------------------------------------------------------------------------------
sys.setrecursionlimit(1000000)

# Creating Class of Maze Cells==========================================================================================
class Cell(object):
    def __init__(self, xpos, ypos):
        self.cellType = "empty"
        self.xpos = xpos
        self.ypos = ypos
        self.g = 0
        self.h = 0
        self.f = 0

    def DisplayText(self,text):
        textRect = text.get_rect()
        textRect.center = (self.xpos + cellSize / 2, self.ypos + cellSize / 2)
        screen.blit(text, textRect)

    def redraw(self):
        x = self.xpos
        y = self.ypos
        if cellSize > 60: #If the cells are big enough, show f, g, and h values
            font = pygame.font.Font(pygame.font.get_default_font(), cellSize/6)
            label = str(self.g) + " " + str(self.h) + " " + str(self.f)
        else:
            font = pygame.font.Font(pygame.font.get_default_font(), cellSize/2)
            label = str(self.f)
        #Cell Types-----------------------------------------------------------------------------------------------------
        if self.cellType == "start":
            pygame.draw.rect(screen, blue, (x, y, cellSize, cellSize))
            font2 = pygame.font.Font(pygame.font.get_default_font(), cellSize/2)
            text = font2.render("S", True, black, blue)
            self.DisplayText(text)
        elif self.cellType == "end":
            pygame.draw.rect(screen, blue, (x, y, cellSize, cellSize))
            font2 = pygame.font.Font(pygame.font.get_default_font(), cellSize/2)
            text = font2.render("F", True, black, blue)
            self.DisplayText(text)
        elif self.cellType == "test": #Cells to test around the parent cell
            pygame.draw.rect(screen, green, (x, y, cellSize, cellSize))
            text = font.render(label, True, black, green)
            self.DisplayText(text)
        elif self.cellType == "prospect": #Cells to move onto to and check others around
            pygame.draw.rect(screen, red, (x, y, cellSize, cellSize))
            text = font.render(label, True, black, red)
            self.DisplayText(text)
        elif self.cellType == "shortest path": #Cells that are part of the shortest path
            pygame.draw.rect(screen, blue, (x, y, cellSize, cellSize))
            text = font.render(label, True, black, blue)
            self.DisplayText(text)
        elif self.cellType == "wall":
            pygame.draw.rect(screen, black, (x, y, cellSize, cellSize))
        #Drawing grid lines that separate cells-------------------------------------------------------------------------
        pygame.draw.line(screen, black, (x, y), (x + cellSize, y))
        pygame.draw.line(screen, black, (x + cellSize, y), (x + cellSize, y + cellSize))
        pygame.draw.line(screen, black, (x, y + cellSize), (x + cellSize, y + cellSize))
        pygame.draw.line(screen, black, (x, y), (x, y + cellSize))


#Function to Set Up Grid and Walls======================================================================================
def GridSetUp(size, numberOfWalls, gridType):
    global grid
    global visited
    global closerCells
    global shortestPath
    global walls
    global solved
    grid = {}
    walls = []
    solved = False
    visited = {start: 0} #open dictionary that stores cells that have been tested in pairs => daughter:parent
    closerCells = [start] #open list that stores cells that are in direction of target and could be on shortest path
    shortestPath = [start] #open list that stores cells on the shortest path
    #Creating 2D Grid Array in a dictionary => (x,y):Cell object--------------------------------------------------------
    for y in range(row):
        for x in range(col):
            grid[(x, y)] = Cell(cellSize * x + 10, cellSize * y + 10)
    #Setting start and end cells----------------------------------------------------------------------------------------
    grid[start].cellType = "start"
    grid[end].cellType = "end"
    #Creating Walls-----------------------------------------------------------------------------------------------------
    #Random Walls
    # random small         random big
    # size = 15            size = 40
    # numberOfWalls = 90   numberOfWalls = 700
    if gridType == "random big" or gridType == "random small":
        for x in range(numberOfWalls):
            while True:
                wall = (random.choice(range(size)), random.choice(range(size)))
                if wall not in walls and wall != start and wall != end:
                    walls.append(wall)
                    grid[wall].cellType = "wall"
                    break
    #Grid type 1 design
    # |     |
    # |-----|
    # |     |
    #size = 20
    elif gridType == "1":
        print "hi"
        for y in range(5,16):
            walls.append((3,y))  #left branch of walls
            walls.append((17,y)) #right branch of walls
            grid[(3, y)].cellType = "wall"
            grid[(17, y)].cellType = "wall"
        for x in range(4,18):
            walls.append((x,10))
            grid[(x, 10)].cellType = "wall"

#Movement Cost Calculation Function=====================================================================================
def MovementCost(parentCell, adjacent):
    g = ((((adjacent[0] - parentCell[0])**2 + (adjacent[1] - parentCell[1])**2) ** (1/2.0))) * 10 #Hypotenuse*10
    g = int(g + grid[parentCell].g) #add movement cost between parent and adjacent to parent's movement cost
    return g                        #this will give movement cost from start to the adjacent cell


#Heuristic Cost Calculaion Function=====================================================================================
def HeuristicCost(end, adjacent):
    h = (abs(end[0] - adjacent[0]) + abs(end[1] - adjacent[1])) * 10  # Manhattan Distance (x dist + y dist)
    return h


#Calculate Cell Costs and Store Costs in Cell Object Function===========================================================
def CalculateCellCosts(parentCell, adjacent, end):
    g = MovementCost(parentCell, adjacent)
    h = HeuristicCost(end, adjacent)
    f = g + h
    grid[adjacent].g = g
    grid[adjacent].h = h
    grid[adjacent].f = f


#Recursive Pathfinding Functions========================================================================================
def FindPath(parentCell): #Takes a cell by its coordinate
    global solved
    x = parentCell[0]
    y = parentCell[1]
    if parentCell not in visited:
        visited[parentCell] = 0
    #Analyzing adjacent cells to parent cell----------------------------------------------------------------------------
    for adjacent in [(x-1,y-1), (x,y-1), (x+1,y-1)
                    ,(x-1, y ), (x, y ), (x+1, y )
                    ,(x-1,y+1), (x,y+1), (x+1,y+1)]:
        if (adjacent in grid) and (adjacent not in walls) and (adjacent not in visited):
            visited[adjacent] = parentCell #Add adjacent to visited and point adjacent to parent cell
            grid[adjacent].cellType = "test"
            CalculateCellCosts(parentCell, adjacent, end)
    #Finding test cell in visited that has the lowest F cost------------------------------------------------------------
    lowestF = [parentCell, 100000000] #[cell coordinate, F cost]
    for cell in visited:
        if (cell not in closerCells) and (grid[cell].f < lowestF[1]):
            lowestF = [cell, grid[cell].f]
    if lowestF == [parentCell, 100000000]: #If trapped and no path to the end, return to other cells
        print "No Solution"
        return
    optimalCell = lowestF[0]
    closerCells.append(optimalCell)
    grid[optimalCell].cellType = "prospect"
    #Updating g and f costs of adjacent cells to parent-----------------------------------------------------------------
    #If current parent is closer to adjacent than its previous parent, update g and f costs of adjacent using new parent
    x = optimalCell[0]
    y = optimalCell[1]
    for adjacent in [(x-1,y-1),( x ,y-1),(x+1,y-1)
                    ,(x-1, y ),( x , y ),(x+1, y )
                    ,(x-1,y+1),( x ,y+1),(x+1,y+1)]:
        if (adjacent in grid) and (adjacent not in walls) and (adjacent in visited):
            testg = MovementCost(optimalCell,adjacent)
            if testg < grid[adjacent].g:
                grid[adjacent].g = testg
                grid[adjacent].f = testg + grid[adjacent].h
                visited[adjacent] = optimalCell
    #If the test cell with the lowest F cost is the end cell, add the parent cell to shortest path list-----------------
    if optimalCell == end:
        grid[end].cellType = "end"
        solved = True
        shortestPath.append(parentCell)
        return
    #Recursive call to run function again with new test cell------------------------------------------------------------
    FindPath(optimalCell)
    #When returning from recursive calls, if daughter is in shortest path, parent must be too---------------------------
    if visited[shortestPath[-1]] == parentCell:
        shortestPath.append(parentCell)


#Function to Display Shortest Path in Blue==============================================================================
def ShowShortestPath():
    shortestPath.remove(start)
    for cell in shortestPath:
        grid[cell].cellType = "shortest path"
    grid[start].cellType = "start"
    print "Shortest Path:",len(shortestPath),"Steps"


#Main===================================================================================================================
pygame.init()
pygame.display.set_caption("A* Algorithm Path Finding")
width = 1200
height = 1200
screen = pygame.display.set_mode([width, height])
clock = pygame.time.Clock()
gridType = "random big"
if gridType == "random big":
    size = 40
    numberOfWalls = 700
    start = (0, 0)
    end = (size - 1, size - 1)
elif gridType == "random small":
    size = 15
    numberOfWalls = 90
    start = (0, 0)
    end = (size - 1, size - 1)
elif gridType == "1":
    size = 20
    numberOfWalls = 50
    start = (10,0)
    end = (10,19)
row = size
col = size
cellSize = int(math.floor((width-20)/size)) #round down
grid = {}
visited = {}
closerCells = []
shortestPath = []
walls = []
solved = False
done = False
black = (0, 0, 0)
green = (50, 220, 80)
white = (255, 255, 255)
blue = (52, 146, 240)
red = (222, 36, 36)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                GridSetUp(size, numberOfWalls, gridType)
            elif event.key == pygame.K_f and solved == False:
                FindPath(start)
            elif event.key == pygame.K_SPACE and solved == True:
                ShowShortestPath()
    screen.fill(white)
    for box in grid.values():
        box.redraw()
    pygame.display.flip()
    clock.tick(30)
