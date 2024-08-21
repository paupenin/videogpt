import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import cv2

# Load the CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Function to preprocess and encode the image
def preprocess_frame(frame):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return processor(images=image, return_tensors="pt")

# Function to encode text
def preprocess_text(text):
    return processor(text=[text], return_tensors="pt")

def extract_frames(video_path: str):
    video_cap = cv2.VideoCapture(video_path)
    frame_rate = video_cap.get(cv2.CAP_PROP_FPS)
    success, frame = video_cap.read()
    frames = []
    timestamps = []

    while success:
        timestamp = video_cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Get timestamp in seconds
        frames.append(frame)
        timestamps.append(timestamp)
        success, frame = video_cap.read()

    video_cap.release()
    return frames, timestamps

def match_query_to_frame(frames, timestamps, query):
    # Encode the query text
    text_inputs = preprocess_text(query)
    
    # Iterate over frames and find the best match
    best_match_time = None
    best_similarity = -1
    for i, frame in enumerate(frames):
        # Preprocess the frame
        image_inputs = preprocess_frame(frame)
        
        # Get image and text embeddings
        with torch.no_grad():
            image_features = model.get_image_features(**image_inputs)
            text_features = model.get_text_features(**text_inputs)
        
        # Compute the similarity between the image and text
        similarity = torch.nn.functional.cosine_similarity(image_features, text_features).item()
        
        # Keep track of the best match
        if similarity > best_similarity:
            best_similarity = similarity
            best_match_time = timestamps[i]  # Use the timestamp instead of the index
    
    return best_match_time
