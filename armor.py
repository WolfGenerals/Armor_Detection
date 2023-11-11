from collections import namedtuple
from math import cos, sin, radians
from typing import Sequence

import cv2
import numpy
from cv2 import Mat
from cv2.typing import Point2f
# from cv2.typing import Point
from numpy import array

Point = tuple[int, int]
BGR = namedtuple("BGR", "b g r")


class LightBar:
    __centre: Point
    __length: float
    __angle: float
    __width: float = 0

    def __init__(self, centre: Point, length: tuple[int, int], angle: float):
        # if isinstance(length, tuple):
        #   if length[0] < length[1]:
        #       self.__width = length[0]
        #       length = length[1]
        #       angle += 90
        #   else:
        #       self.__width = length[1]
        #       length = length[0]

        if angle < 45:
            self.__width = length[0]
            self.__length = length[1]
            self.__centre = centre
            self.__angle = angle+90
        else:
            self.__width = length[1]
            self.__length = length[0]
            self.__centre = centre
            self.__angle = angle

    @property
    def legal(self) -> bool:
        angle = abs(self.angle - 90) < 20
        width = 0.1 < self.__width / self.length < 1.1
        return angle and width

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
        return (
            int(self.centre[0] + cos(radians(self.angle)) * self.length / 2),
            int(self.centre[1] + sin(radians(self.angle)) * self.length / 2)
        )

    @property
    def lowerPoint(self) -> Point:
        return (
            int(self.centre[0] - cos(radians(self.angle)) * self.length / 2),
            int(self.centre[1] - sin(radians(self.angle)) * self.length / 2)
        )

    def draw(self, image: Mat):
        cv2.line(image, self.upperPoint, self.lowerPoint, BGR(0, 200, 0), thickness=5)


class Armor:
    __leftBar: LightBar
    __rightBar: LightBar

    def __init__(self, bar1: LightBar, bar2: LightBar):
        self.__leftBar, self.__rightBar = sorted([bar1, bar2], key=lambda x: x.centre[0])

    @property
    def legal(self) -> bool:
        angle = abs(self.__rightBar.angle - self.__leftBar.angle) < 5
        length = 0.65 < self.__leftBar.length / self.__rightBar.length < 1.53
        distance = 0.3 < (abs(self.__leftBar.centre[0] - self.__rightBar.centre[0]) +
                          abs(self.__leftBar.centre[1] - self.__rightBar.centre[1])) / (
                           self.__leftBar.length + self.__rightBar.length) < 4
        height = abs((self.__leftBar.centre[1] - self.__rightBar.centre[1]) /
                     (self.__leftBar.length + self.__rightBar.length)) < 1
        return angle and distance and length and height

    @property
    def points(self) -> tuple[Point, Point, Point, Point]:
        return (
            (
                int(self.__rightBar.centre[0] + cos(radians(self.__rightBar.angle)) * self.__rightBar.length),
                int(self.__rightBar.centre[1] + sin(radians(self.__rightBar.angle)) * self.__rightBar.length)
            ),
            (
                int(self.__leftBar.centre[0] + cos(radians(self.__leftBar.angle)) * self.__leftBar.length),
                int(self.__leftBar.centre[1] + sin(radians(self.__leftBar.angle)) * self.__leftBar.length)
            ),
            (
                int(self.__leftBar.centre[0] - cos(radians(self.__leftBar.angle)) * self.__leftBar.length),
                int(self.__leftBar.centre[1] - sin(radians(self.__leftBar.angle)) * self.__leftBar.length)
            ),
            (
                int(self.__rightBar.centre[0] - cos(radians(self.__rightBar.angle)) * self.__rightBar.length),
                int(self.__rightBar.centre[1] - sin(radians(self.__rightBar.angle)) * self.__rightBar.length)
            ),
        )

    def draw(self, image: Mat):
        n = array([array([int(i) for i in p]) for p in self.points])
        cv2.drawContours(image, array((n,)), 0, BGR(255, 0, 255), thickness=2)


def getLightImage(img) -> Mat:
    imageLights: Mat = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, imageLights = cv2.threshold(imageLights, 200, 255, cv2.CV_8U)
    # imageLights = cv2.erode(imageLights, numpy.ones((3, 3)), iterations=1)
    # imageLights = cv2.dilate(imageLights, numpy.ones((3, 3)), iterations=1)
    return imageLights


def getLightBar(contours: Sequence[Mat]) -> list[LightBar]:
    lightBars: list[LightBar] = []
    for contour in contours:
        if contour.size < 3:
            continue
        rect = cv2.minAreaRect(contour)
        if not 0<rect[2]<=90:
            continue
        lightBar = LightBar(*rect)
        if lightBar.legal:
            lightBars.append(lightBar)
    return lightBars


def getArmor(lightBars: Sequence[LightBar]) -> list[Armor]:
    armors: list[Armor] = []
    for i in range(len(lightBars)):
        for j in range(i + 1, len(lightBars)):
            armor = Armor(lightBars[i], lightBars[j])
            if armor.legal:
                armors.append(armor)
    return armors
