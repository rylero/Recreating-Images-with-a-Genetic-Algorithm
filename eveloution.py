import threading
from PIL import Image, ImageDraw
import numpy as np
import random
from queue import Queue
from math import sqrt

from regex import R

# (((x,y), rad), sides, rot, fill)
count = 0

imageToRecreate = Image.open(input("File Name:"))
imageToRecreatePix = imageToRecreate.load()
WIDTH, HEIGHT = imageToRecreate.size

canvasImg = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
canvasImgPix = canvasImg.load()
canvas = ImageDraw.Draw(canvasImg)

def sampleColorRadius(imagePix, x, y, rad):
    r, g, b, i = 0, 0, 0, 0
    for row in range(x-rad, x+rad):
        for col in range(y-rad, y+rad):
            pix = imagePix[row,col]
            r += pix[0]
            g += pix[1]
            b += pix[2]
            i+=1
    return (r//i, g//i, b//i)

def generateSemiRandomPolyGon(imageToRecreatePix):
    rad = int(random.randint(1, (HEIGHT/2)-1))
    x = int(random.randint(rad, (WIDTH-1)-rad))
    y = int(random.randint(rad, (HEIGHT-1)-rad))
    sides = int(random.randint(3, 15))
    rot = int(random.randint(0, 360))
    fill = sampleColorRadius(imageToRecreatePix, x, y, rad)
    return [[[x,y], rad], sides, rot, fill, -1]

def displayPolygon(canvas, settings): # [((x,y), radius), numSides, rot, fill]
    canvas.regular_polygon(settings[0], settings[1], settings[2], fill=settings[3])

def evaluateCanvas(canvasImg, canvasImgPix, imageToRecreatePix): # images must be the same size
    width, height = canvasImg.size
    diff = 0
    # loop through every pixel
    for x in range(width):
        for y in range(height):
            pix1 = canvasImgPix[x,y]
            pix2 = imageToRecreatePix[x,y]
            # calculate the difference in color
            d=sqrt((pix2[0]-pix1[0])**2+(pix2[1]-pix2[1])**2+(pix2[2]-pix2[2])**2)
            diff += d * d
    difference = 1 - diff / (width * height * 4 * 256 * 256)
    return difference

def evaluateShape(canvasImg, imageToRecreatePix, shapeSettings):
    ogImgCopy = canvasImg.copy()
    ogImgPixCopy = ogImgCopy.load()
    ogImgDrawCopy = ImageDraw.Draw(ogImgCopy)
    displayPolygon(ogImgDrawCopy, shapeSettings)
    return evaluateCanvas(ogImgCopy, ogImgPixCopy, imageToRecreatePix)

def generateChild(parent):
    # take averages of mother and father and add random mutation
    # np.clip clamps the value so the shape dosent go off screen
    rad = int(np.clip(parent[0][1] + random.randint(-5, 5), 1, HEIGHT/2))
    x = int(np.clip(parent[0][0][0] + random.randint(-5, 5), rad, WIDTH-rad))
    y = int(np.clip(parent[0][0][1] + random.randint(-5, 5), rad, HEIGHT-rad))
    sides = int(np.clip(parent[1] + random.randint(-2, 2), 3, 15))
    rot = int(np.clip(parent[2] + random.randint(-5, 5), 0, 360))
    r = int(np.clip(parent[3][0] + random.randint(-5, 5), 0, 360))
    g = int(np.clip(parent[3][1] + random.randint(-5, 5), 0, 360))
    b = int(np.clip(parent[3][2] + random.randint(-5, 5), 0, 360))
    # return the child shape with the average values
    return [[[x, y], rad], sides, rot, (r, g, b), -1]

def addEveloutionBasedShapeToCanvas(canvasImg, imageToRecreatePix, canvas):
    currentShapes = [generateSemiRandomPolyGon(imageToRecreatePix) for i in range(0,50)]

    for i in range(0, 3):
        #print("Generation", str(i+1), "has started")

        for shape in currentShapes:
            e = evaluateShape(canvasImg, imageToRecreatePix, shape)
            shape[4] = e
        
        #print("Shapes have been evaluated")

        shapes = sorted(currentShapes, key=lambda x: x[4])[::-1][0:10][::-1]
        currentShapes.clear()

        #print("Shapes have been sorted")

        possibleParents = []
        for i in range(0, len(shapes)):
            for j in range(0, i):
                possibleParents.append(shapes[i])
        
        #print("Parents have been created")
                
        for i in range(0, 50):
            p1 = random.choice(possibleParents)
            currentShapes.append(generateChild(p1))
        
        #print("Children have been created")

    bestShape = currentShapes[0]
    bestShapeFit = evaluateShape(canvasImg, imageToRecreatePix, bestShape)

    for shape in currentShapes:
        e = evaluateShape(canvasImg, imageToRecreatePix, shape)
        shape[4] = e
        if e > bestShapeFit:
            bestShape = shape
            bestShapeFit = e

    displayPolygon(canvas, bestShape)

def workerThread(queue):
    global count
    print("Thread Has Been Initialized...")
    while not queue.empty():
        func = queue.get()
        if func == 0:
            addEveloutionBasedShapeToCanvas(canvasImg, imageToRecreatePix, canvas)
            count += 1
            print("Shape generated. Shape:", count, "Evaluation:", evaluateCanvas(canvasImg, canvasImgPix, imageToRecreatePix))


workerThreads = []
threadQueue = Queue()

print("Initializing Queue...")
for i in range(0, 3000):
    threadQueue.put(0)

print("Starting Threads...")
for i in range(0, 5):
    t = threading.Thread(target=workerThread, args=(threadQueue,))
    t.start()
    workerThreads.append(t)


#print(evaluateCanvas(canvasImg, canvasImgPix, imageToRecreatePix))
#addEveloutionBasedShapeToCanvas(canvasImg, imageToRecreatePix, canvas)
#print(evaluateCanvas(canvasImg, canvasImgPix, imageToRecreatePix))

while not threadQueue.empty():
    continue

canvasImg.save("img.png")
canvasImg.show()
quit()