import numpy as np
import pandas as pd

from PIL import Image
import cv2

from time import perf_counter
import datetime

import os
from os.path import join
import sys

startTime = perf_counter()

sys.setrecursionlimit(15000)

def createFolder(cwd, fps, grid, k) -> str:
    # Getting Current Time
    curr = datetime.datetime.now()
    dateStr = str(curr.date())
    timeStr = str(curr.time())

    # Folder Name
    directory = "Grid_GOL_RUN_" + dateStr.replace('-', '_') + "_" + timeStr.replace('-', '_').replace(':','_')

    # Final Path
    fPath = os.path.join(cwd, directory)

    # Creating a Directory
    os.mkdir(fPath)

    # Creating the Images SubFolder
    imgPath = os.path.join(fPath, "Images")

    # Creating the CSVs subfloder
    csvPath = os.path.join(fPath, "CSVs")

    os.mkdir(imgPath)
    os.mkdir(csvPath)

    # Writing the useful files

    # Saving the initial grid state
    np.savetxt(fname = os.path.join(fPath, 'initialState.csv'), 
               X = grid, delimiter = ',', fmt='%d')
    
    info = """
    author: S.Jaidheer
    github: JAIDHEER007

    Path finding using Python

    INFO
    ==============================================================
    Date: {fdate}
    time: {ftime}

    Rows: {frows}
    Cols: {fcols}
    Zoom Factor: {k}

    Set FPS: {ffps}
    """

    with open(os.path.join(fPath, 'info.txt'), 'w') as fileHandle:
        fileHandle.writelines(info.format(fdate = dateStr, ftime = timeStr, 
                              frows = grid.shape[0], fcols = grid.shape[1],
                              ffps = fps, k = k))
        
    return fPath

class grid:
    def __init__(self, npgrid, fPath, zFactor = 1, updateFunction = None):
        self.__npgrid = npgrid 
        self.__fPath = fPath
        self.__zFactor = zFactor
        self.__updateFunction = updateFunction

    def get(self, coordinates):
        return self.__npgrid[coordinates]

    def set(self, coordinates, value):
        self.__npgrid[coordinates] = value
        return self.__updateFunction(self.__npgrid, self.__fPath, self.__zFactor) if self.__updateFunction is not None else None

    def getShape(self): 
        return self.__npgrid.shape

class solver:
    def isValid(shape, coordinates) -> bool:
        rows, cols = shape
        i, j = coordinates
        return (i >= 0) and (i < rows) and (j >= 0) and (j < cols)

    def dfs(grid, coordinates):
        # If the coordinates are out of maze then return false
        if not solver.isValid(grid.getShape(), coordinates): return False

        gridState = grid.get(coordinates)

        # Check if the coordinates are end point
        if gridState == 3:
            print(coordinates)
            return True

        # if the coordinates are representing a wall then return False
        if gridState == 1: return False

        # if the coordinates are previously visited then return False
        if gridState == 4: return False

        # Now make the element at specified coordinates visited
        grid.set(coordinates, 4)

        # Traverse the grid in 4 directions
        
        #left 
        if solver.dfs(grid, (coordinates[0] + 0, coordinates[1] + 1)): return True
        # right
        if solver.dfs(grid, (coordinates[0] + 0, coordinates[1] - 1)): return True
        # up
        if solver.dfs(grid, (coordinates[0] + 1, coordinates[1] + 0)): return True
        # down
        if solver.dfs(grid, (coordinates[0] - 1, coordinates[1] + 0)): return True

        # grid.set(coordinates, gridState)

        return False

cwd = sys.path[0]
# cwd = f"/content/drive/MyDrive/PathFinding/TEST"

# Setting the Zoom Factor
zFactor = 20

# Getting The Grid
url = 'State175_13.csv'
npgrid = pd.read_csv(url, header=None, dtype=int).to_numpy()


#Folder Path
fPath = createFolder(cwd = cwd, fps =35, grid = npgrid, k = zFactor)

count = 0
colors = [(0,0,0), (255, 255, 255), (255, 255, 0), (255, 0, 0), (0, 0, 255)]
def save(npgrid, fPath, zFactor):
    imgPath = os.path.join(fPath, 'Images')
    csvPath = os.path.join(fPath, 'CSVs')

    oldShape = npgrid.shape
    newNpGrid = np.zeros((oldShape[0] * zFactor, oldShape[1] * zFactor, 3), dtype=np.uint8)
    newShape = newNpGrid.shape

    for i in range(newShape[0]):
        for j in range(newShape[1]):
            newNpGrid[(i, j)] = colors[npgrid[(i // zFactor , j // zFactor)]]


    img = Image.fromarray(newNpGrid, mode="RGB")

    global count

    # Saving the Image to Images subfolder
    img.save(os.path.join(imgPath, 'Img{cnt}.png'.format(cnt = count)))

    # Saving the CSVs to CSV subfolder
    np.savetxt(fname = os.path.join(csvPath, 'State{cnt}.csv'.format(cnt = count)), 
                X = npgrid, delimiter = ',', fmt="%d")
    
    # Update the count
    count += 1

# Creating the grid object
gridObj = grid(npgrid, fPath, zFactor, save)

print(gridObj.getShape())

startingLocation = (0, 8)
endingLocation = (173,5)

if not solver.isValid(gridObj.getShape(), startingLocation):
  raise Exception("Starting Location Outside the grid")
if not solver.isValid(gridObj.getShape(), endingLocation):
  raise Exception("Ending Location Outside the grid")

gridObj.set(startingLocation, 2)
gridObj.set(endingLocation, 3)

solver.dfs(gridObj, startingLocation)

endTime = perf_counter()

print(endTime - startTime)