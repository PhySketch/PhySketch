import cv2 as cv
import numpy as np

def rotate_bound_center(image, angle,center):
    print(image.shape,center)

    padX = [image.shape[1] - int(center.x), int(center.x)]
    padY = [image.shape[0] - int(center.y), int(center.y)]
    #print(padX,padY)
    imgP = np.pad(image, (padY,padX,[0,0]), 'constant')
    #cv.imshow("oi",imgP)
    imgR = rotate_bound(imgP,angle)#ndimage.rotate(imgP, -angle, reshape=False)

    return imgR[padY[0]: -padY[1], padX[0]: -padX[1]]



def rotate_bound(image, angle,borderValue=0):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv.warpAffine(image, M, (nW, nH),borderValue=borderValue)