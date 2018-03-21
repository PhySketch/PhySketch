from darkflow.net.build import TFNet
import cv2

options = {"model": "/Users/zulli/Desktop/PhySketch/src/prediction/darknet/cfg/tiny-yolo-voc-psk.cfg",
           "load":186, "threshold": 0.01}

tfnet = TFNet(options)

img = cv2.imread("/Users/zulli/Desktop/PhySketch/Dataset/cropped/IMG00000_2.png")
result = tfnet.return_predict(img)

tl = (result[0]['topleft']['x'], result[0]['topleft']['y'])
br = (result[0]['bottomright']['x'], result[0]['bottomright']['y'])
label = result[0]['label']

img = cv2.rectangle(img, tl, br, (0, 255, 0), 7)
img = cv2.putText(img, label, tl, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)
cv2.imshow("alo",img)
print(result)
cv2.waitKey(0)