from darkflow.net.build import TFNet
import cv2
import math
import json
import numpy as np
options = {"model": "/Users/zulli/Documents/PhySketch/physketch/prediction/prediction/cfg/tiny-yolo-voc-psk.cfg",
           "load":1364, "threshold": 0.1}

tfnet = TFNet(options)

for i in range(100):
    img = cv2.imread("/Users/zulli/Documents/PhySketch/Dataset/generated/cropped/SC"+str(i)+".png")
    '''img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    cv2.imshow('a', img)
    boundaries = [
        ([0, 0, 0], [180, 255, 50]),
        ([0, 0, 50], [10, 255, 255])
    ]
    result = []
    i=0

    for (lower, upper) in boundaries:
        # create NumPy arrays from the boundaries
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(img, lower, upper)
        output = cv2.bitwise_and(img, img, mask=mask)

        #result.extend(tfnet.return_predict(output))
        cv2.imshow(str(i),output)
        i+=1
    cv2.waitKey(0)
    '''

    result = tfnet.return_predict(img)
    for j,r in enumerate(result):
        tl = (r['topleft']['x'], r['topleft']['y'])
        br = (r['bottomright']['x'], r['bottomright']['y'])
        label = r['label'] +' '+"{0:.2f}".format(r['confidence'])
        img = cv2.rectangle(img, tl, br, (0, 255, 0), math.ceil(7*float(r['confidence'])))
        img = cv2.putText(img, label, tl, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)
        result[j]['confidence'] = float(result[j]['confidence'])

    cv2.imwrite("/Users/zulli/Documents/PhySketch/Dataset/generated/predict/SC"+str(i)+".png",img)
    with open("/Users/zulli/Documents/PhySketch/Dataset/generated/predict/SC"+str(i)+".json",mode="w") as f:
        f.write(json.dumps(result))

    print(i, result)

#cv2.waitKey(0)