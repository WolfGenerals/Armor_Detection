from typing import Sequence

import cv2
import numpy
from cv2 import Mat
from numpy import array


def drawRect(img: Mat, rect: tuple[Sequence[float], Sequence[int], float]):
    rotated_rect = cv2.RotatedRect(rect[0], rect[1], rect[2])
    rect_points: Sequence[Sequence[float]] = rotated_rect.points()
    contour = array([array([int(i) for i in p]) for p in rect_points])
    cv2.drawContours(img, array([contour]), 0, (0, 255, 0), thickness = 2)


def rectL(rect: tuple[Sequence[float], Sequence[int], float]):
    return max(rect[1][0], rect[1][1])


def rectW(rect: tuple[Sequence[float], Sequence[int], float]):
    return min(rect[1][0], rect[1][1])


def rectAngle(rect: tuple[Sequence[float], Sequence[int], float]):
    if rect[1][0] < rect[1][1]:
        return rect[2] + 90
    return rect[2]


def isArmorLight(rect: tuple[Sequence[float], Sequence[int], float]):
    length = 1.5 < (rectL(rect) / rectW(rect)) < 8
    angle = abs(rectAngle(rect) - 90) < 10
    return length and angle


def isArmorLightPair(rect1: tuple[Sequence[float], Sequence[int], float],
                     rect2: tuple[Sequence[float], Sequence[int], float]) -> bool:
    angleInRange = abs(rectAngle(rect1) - rectAngle(rect2)) < 2
    lengthInRange = 0.66 < (rectL(rect1) / rectL(rect2)) < 1.5
    return angleInRange and lengthInRange


def getLightImage(img):
    imageLights: Mat = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, imageLights = cv2.threshold(imageLights, 160, 255, cv2.CV_8U)
    imageLights = cv2.erode(imageLights, numpy.ones((3, 3)), iterations = 1)
    imageLights = cv2.dilate(imageLights, numpy.ones((3, 3)), iterations = 1)
    # imageLights = cv2.erode(imageLights, numpy.ones((5, 5)), iterations = 1)
    # imageLights = cv2.dilate(imageLights, numpy.ones((5, 5)), iterations = 2)
    # imageLights = cv2.erode(imageLights, numpy.ones((5, 5)), iterations = 1)
    # imageLights = cv2.dilate(imageLights, numpy.ones((5, 5)), iterations = 1)
    # imageLights = cv2.erode(imageLights, numpy.ones((5, 5)), iterations = 1)
    return imageLights


def getLightPair(rects):
    pair = []
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if not isArmorLightPair(rects[i], rects[j]):
                continue
            pair.append((rects[i], rects[j]))
    return pair


def getLights(contours):
    rects: list[tuple[Sequence[float], Sequence[int], float]] = []
    for contour in contours:
        rect = cv2.minAreaRect(contour)
        if isArmorLight(rect):
            rects.append(rect)
    return rects
