from fastapi import APIRouter, FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from azure.storage.blob import BlobServiceClient
from ultralytics import YOLO
import cv2
import numpy as np
import io
import pytesseract
from app.config.settings import get_settings
from pathlib import Path
pytesseract.pytesseract.tesseract_cmd = Path(__file__).parent / 'ocr' / 'tesseract.exe'
from PIL import ImageFont, ImageDraw, Image

webcam_router = APIRouter(
    prefix='/api/webcam',
    tags=['webcam'],
    responses={404: {"description": "Not found"}},
)

# Load YOLO model
settings = get_settings()
model = YOLO("app/model_weights/yolo11s.pt")  # Update with the path to your YOLOv8 model

# Class names in the model
class_names = [
    "person", "bicycle", "car", "motorcycle", "airplane", 
    "bus", "train", "truck"
]

# List of allowed class indices for detection
allowed_classes = [0, 1, 2, 3, 5, 7]

# Unique ID tracking
object_id_counter = 0
tracked_objects = {}

# Setup Azure Blob Storage client
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
container_name = settings.AZURE_CONTAINER_NAME

# Tracking parameters
max_missing_frames = 5  # Maximum number of frames to consider an object lost
proximity_threshold = 50  # Pixels distance threshold to match objects

@webcam_router.get("/")
async def get_camera_page():
    return HTMLResponse(open("app/template/camera.html").read())

# Load YOLO model for license plate detection
license_plate_model = YOLO("app/model_weights/license_platev1nbest.pt")  # Update with the path to your license plate model

@webcam_router.post("/predict-frame")
async def predict_frame(file: UploadFile = File(...)):
    global object_id_counter, tracked_objects
    
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Perform object detection for primary model
    results = model(frame)
    detections = results[0]

    new_tracked_objects = {}

    # Increment missing frame count for existing tracked objects
    for object_id, obj in tracked_objects.items():
        obj['missing_frames'] += 1

    # Process detections
    for detection in detections.boxes:
        cls = int(detection.cls[0])
        confidence = float(detection.conf[0])

        if cls in allowed_classes:
            x1, y1, x2, y2 = map(int, detection.xyxy[0])
            label = class_names[cls]

            # Draw bounding box for allowed classes
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Process vehicles for license plate detection
            if label in ["car", "motorcycle", "truck", "bus"]:
                vehicle_crop = frame[y1:y2, x1:x2]
                lp_results = license_plate_model(vehicle_crop)
                lp_detections = lp_results[0]

                for lp_detection in lp_detections.boxes:
                    lp_x1, lp_y1, lp_x2, lp_y2 = map(int, lp_detection.xyxy[0])
                    lp_confidence = float(lp_detection.conf[0])

                    lp_x1 += x1
                    lp_y1 += y1
                    lp_x2 += x1
                    lp_y2 += y1

                    # Crop and process the license plate
                    license_plate_crop = frame[lp_y1:lp_y2, lp_x1:lp_x2]
                    gray_plate = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)

                    # OCR with Thai and English support
                    ocr_text = pytesseract.image_to_string(
                        gray_plate, 
                        config='--psm 8 -l tha+eng'
                    ).strip()

                    # Draw bounding box for the license plate
                    cv2.rectangle(frame, (lp_x1, lp_y1), (lp_x2, lp_y2), (255, 0, 0), 2)

                    # Draw stroked text using PIL
                    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(frame_pil)
                    font = ImageFont.truetype("/angsana.ttc", 20)

                    # Draw stroke
                    stroke_color = (0, 0, 0)  # Black color for stroke
                    offsets = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
                    for offset in offsets:
                        draw.text((lp_x1 + offset[0], lp_y1 - 10 + offset[1]), f"License Plate: {ocr_text}", font=font, fill=stroke_color)

                    # Draw main text
                    draw.text((lp_x1, lp_y1 - 10), f"License Plate: {ocr_text}", font=font, fill=(255, 0, 0))

                    # Convert back to OpenCV image
                    frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    # Update tracked objects and handle missing ones
    for object_id, obj in list(tracked_objects.items()):
        if obj['missing_frames'] > max_missing_frames:
            del tracked_objects[object_id]
        else:
            new_tracked_objects[object_id] = obj

    tracked_objects = new_tracked_objects

    # Encode frame to JPEG for streaming
    _, jpeg = cv2.imencode('.jpg', frame)
    return StreamingResponse(io.BytesIO(jpeg.tobytes()), media_type="image/jpeg")


@webcam_router.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
    await blob_client.upload_blob(file.file, overwrite=True)
    return JSONResponse(content={"message": f"File {file.filename} uploaded successfully."})

# Helper function to calculate Intersection over Union (IoU)
def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

# Main FastAPI app
app = FastAPI()
app.include_router(webcam_router)
