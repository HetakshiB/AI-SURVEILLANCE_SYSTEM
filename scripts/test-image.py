from ultralytics import YOLO
import cv2

# Load your trained model
model = YOLO("best.pt")   # make sure best.pt is in same folder

# Test image path
image_path = "test images/knife1.png"

# Run inference
results = model(image_path)

# Show result
for r in results:
    img = r.plot()   # draws bounding boxes
    cv2.imshow("Detection", img)

cv2.waitKey(0)
cv2.destroyAllWindows()