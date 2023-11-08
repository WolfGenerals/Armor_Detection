import cv2
from cv2 import Mat

from armor import drawRect, getLightPair, getLightImage, getLights


def main(img: Mat) -> Mat:
    imageLights = getLightImage(img)

    contours, _ = cv2.findContours(imageLights, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rects = getLights(contours)

    draw = img.copy()

    pair = getLightPair(rects)
    for p in pair:
        drawRect(draw, p[0])
        drawRect(draw, p[1])

    return draw


# cv2.namedWindow("in")
# cv2.namedWindow("debug")
# cv2.namedWindow("out")
capture = cv2.VideoCapture('/mnt/e/8-11东大2No.4.avi')
for _ in range(60*60*5+60*40):
    capture.read()

while capture.isOpened():
    flag, img = capture.read()
    if not flag:
        break
    cv2.imshow("in", img)
    cv2.imshow("debug", getLightImage(img))
    cv2.imshow("out", main(img))
    cv2.waitKey(75)
