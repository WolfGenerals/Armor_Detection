from typing import Any, Sequence

import cv2
from cv2 import Mat
from numpy import ndarray, dtype, generic

from armor import getArmor, getLightImage, getLightBar


def main(img: Mat) -> Mat:
    imageLights = getLightImage(img)

    contours: Sequence[Mat] = cv2.findContours(imageLights, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    lightBars = getLightBar(contours)

    draw = img.copy()

    armors = getArmor(lightBars)

    for armor in armors:
        armor.draw(draw)
    for lightBar in lightBars:
        lightBar.draw(draw)
    return draw


if __name__ == '__main__':
    cv2.imshow('233', cv2.imread('Blue-5.jpeg'))
    cv2.imshow('233-g', getLightImage(cv2.imread('Blue-5.jpeg')))
    cv2.imshow('233-o', main(cv2.imread('Blue-5.jpeg')))
    cv2.waitKey(1000)
    capture = cv2.VideoCapture('/mnt/e/8-11东大2No.4.avi')
    for _ in range(60 * 60 * 5 + 60 * 40):
        capture.read()

    while capture.isOpened():
        flag, img = capture.read()
        if not flag:
            break
        cv2.imshow("in", img)
        cv2.imshow("debug", getLightImage(img))
        cv2.imshow("out", main(img))
        cv2.waitKey(120)
