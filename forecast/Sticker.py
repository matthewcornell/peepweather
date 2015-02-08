# an exploration of using http://pillow.readthedocs.org/ to change each hourly color cell from a solid square to
# one that has three mini 'columns' with three tiny gray horizontal lines showing L, M, or H for each of the three
# parameters, say T, W, and P from left to right

from PIL import Image
from PIL import ImageDraw
import random


def makeSqare(thumbSize, hourDes):  # H_DES_LOW, ...
    color = HOUR_DESIRABILITY_TO_COLOR[hourDes]
    return Image.new('RGB', (thumbSize, thumbSize), color=color)


def drawParamBars(image, tempDes, windDes, precipDes):  # P_DES_LOW, ... for each param
    draw = ImageDraw.Draw(image)
    drawParamAtColumn(draw, tempDes, 0)
    drawParamAtColumn(draw, windDes, 1)
    drawParamAtColumn(draw, precipDes, 2)


def drawParamAtColumn(drawImage, paramDesirability, columnNum):  # P_DES_LOW, ...
    imWidth = drawImage.im.size[0]
    imHeight = drawImage.im.size[1]
    colWidth = imWidth / 3
    paramDesToY = {P_DES_LOW: imHeight - 2,
                   P_DES_MED: (imHeight / 2) - 1,
                   P_DES_HIGH: 0}
    lineStartPt = (columnNum * colWidth, paramDesToY[paramDesirability])
    drawImage.rectangle([lineStartPt, (lineStartPt[0] + colWidth, lineStartPt[1] + 1)],
                        fill='lightgray')


thumbSize = 32

def showOne():
    s1 = makeSqare(thumbSize, H_DES_LOW)
    drawParamBars(s1, P_DES_LOW, P_DES_MED, P_DES_HIGH)  # temp, wind, precip
    s1.show()


showOne()


def makeFinalImage():
    numCols, numRows = 7, 13
    finalImage = Image.new('RGB', (thumbSize * numCols + 1, thumbSize * numRows + 1), color='white')
    # draw random hours
    for rowNum in range(numRows + 1):
        for colNum in range(numCols + 1):
            hourDes = random.choice([H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH])
            hourImage = makeSqare(thumbSize, hourDes)
            tempDes = random.choice([P_DES_LOW, P_DES_MED, P_DES_HIGH])
            windDes = random.choice([P_DES_LOW, P_DES_MED, P_DES_HIGH])
            precipDes = random.choice([P_DES_LOW, P_DES_MED, P_DES_HIGH])
            drawParamBars(hourImage, tempDes, windDes, precipDes)  # temp, wind, precip
            finalImage.paste(hourImage, (colNum * thumbSize, rowNum * thumbSize))
    # draw grid - horiz row lines then vert col lines
    draw = ImageDraw.Draw(finalImage)
    for rowNum in range(numRows):
        draw.line([(0, rowNum * thumbSize), (finalImage.size[0], rowNum * thumbSize)],
                  fill='black')
    for colNum in range(numCols):
        draw.line([(colNum * thumbSize, 0), (colNum * thumbSize, finalImage.size[1])],
                  fill='black')
    # done
    return finalImage


fim = makeFinalImage()
fim.show()
