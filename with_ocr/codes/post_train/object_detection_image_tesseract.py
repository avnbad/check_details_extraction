import cv2
import numpy as np
import tensorflow as tf
import pytesseract

# Load the pre-trained model
model_path = 'E:/Projects/Object_detection/check_ocr/results/model/saved_model'
model = tf.saved_model.load(model_path)

# Create a function to perform object detection
def perform_object_detection(image):
    input_tensor = tf.convert_to_tensor(image)
    
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = model(input_tensor)

    return detections

# Load an image for object detection
expected_size = (512,512)
threshold = .3
image_path = '8.JPG'
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
dim = image_rgb.shape[0:2]
image_np = cv2.resize(image_rgb, expected_size)

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\raheel.Zuberi\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

# Perform object detection
detections = perform_object_detection(image_np)

num_detections = int(detections.pop('num_detections'))
detections = {key: value[0, :num_detections].numpy()
            for key, value in detections.items()}
detections['num_detections'] = num_detections

# detection_classes should be ints.
detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

boxes=(detections['detection_boxes'])
classes =(detections['detection_classes'])
scores = (detections['detection_scores'])
            
cls = classes.tolist()

dets = []
for i, value in enumerate(cls):
    if scores[i] > threshold:
        (y1, x1) = (boxes[i][0], boxes[i][1])
        (y2, x2) = (boxes[i][2], boxes[i][3])                        
        dets.append([x1,y1,x2,y2,scores[i],cls[i]])

for variables in dets :
    x1, y1, x2, y2, score, cls = variables

    #rescaling  to original dim
    pt1 = (int(x1 * dim[1]), int(y1 * dim[0])) 
    pt2 = (int(x2 * dim[1]), int(y2 * dim[0]))

    # Extract the ROI for OCR
    roi = image[pt1[1]:pt2[1], pt1[0]:pt2[0]]

    # Perform OCR using pytesseract
    result = pytesseract.image_to_string(roi)

    # Extract text from pytesseract result
    text = result if result else ""
    
    # Draw the bounding box
    cv2.rectangle(image, pt1, pt2, (0, 255,0), 1)
    #cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

    # Display the OCR result
    cv2.putText(image, text, (pt1[0], pt1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow('Object Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
