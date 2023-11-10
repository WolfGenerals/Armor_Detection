from collections import namedtuple
from math import cos, sin, radians
from typing import Sequence

import cv2
import numpy
from cv2 import Mat
# from cv2.typing import Point
from numpy import array

Point = namedtuple("Point", "x y")
BGR = namedtuple("Point", "b g r")


class LightBar:
    __centre: Point
    __length: float
    __angle: float

    def __new__(cls, centre: Point, size: tuple[int, int], angle: float):


    def __init__(self, centre: Point, length: int | tuple[int, int], angle: float):
        if isinstance(length,tuple):
            if length[0] < length[1]:
                length=length[1]
                angle += 90
            else:
                length=length[0]

        self.__centre = centre
        self.__length = length
        self.__angle = angle

    @property
    def legal(self) -> bool:
        angle = abs(self.angle - 90) > 15
        return angle

    @property
    def centre(self) -> Point:
        return self.__centre

    @property
    def length(self) -> float:
        return self.__length

    @property
    def angle(self) -> float:
        return self.__angle

    @property
    def upperPoint(self) -> Point:
        return self.centre[0] + cos(radians(self.angle)) * self.length / 2, self.centre[1] + sin(
            radians(self.angle)) * self.length / 2

    @property
    def lowerPoint(self) -> Point:
        return self.centre[0] - cos(radians(self.angle)) * self.length / 2, self.centre[1] - sin(
            radians(self.angle)) * self.length / 2

    def draw(self, image: Mat):
        cv2.line(image, self.upperPoint, self.lowerPoint, BGR(0, 200, 0), thickness=5)


class Armor:
    leftBar: LightBar
    rightBar: LightBar

    def __init__(self, bar1: LightBar, bar2: LightBar):
        self.leftBar, self.rightBar = sorted([bar1, bar2], key=lambda x: x.centre[0])


def drawRect(img: Mat, rect: tuple[Sequence[float], Sequence[int], float]):
    rotated_rect = cv2.RotatedRect(*rect)
    rect_points: Sequence[Sequence[float]] = rotated_rect.points()
    contour = array([array([int(i) for i in p]) for p in rect_points])
    cv2.drawContours(img, array([contour]), 0, BGR(0, 255, 0), thickness=2)


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
    imageLights = cv2.erode(imageLights, numpy.ones((3, 3)), iterations=1)
    imageLights = cv2.dilate(imageLights, numpy.ones((3, 3)), iterations=1)
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
