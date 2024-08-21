import os
import uuid
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from video_search import extract_frames, match_query_to_frame 

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the storage directory
STORAGE_DIR = "media"
# Ensure the storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

# GET /media/{video_path} to get the video files.
@app.get("/media/{video_path:path}")
async def stream_video(video_path: str, request: Request):
    video_file_path = os.path.join(STORAGE_DIR, video_path)
    
    if not os.path.exists(video_file_path):
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = os.path.getsize(video_file_path)
    range_header = request.headers.get('range')
    if range_header:
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
    else:
        start = 0
        end = file_size - 1

    headers = {
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Accept-Ranges': 'bytes',
        'Content-Length': str(end - start + 1),
        'Content-Type': 'video/mp4',
    }

    async def video_streamer(start: int, end: int, path: str):
        with open(path, 'rb') as video_file:
            video_file.seek(start)
            while start <= end:
                chunk_size = min(4096, end - start + 1)
                data = video_file.read(chunk_size)
                if not data:
                    break
                start += len(data)
                yield data

    return StreamingResponse(video_streamer(start, end, video_file_path), headers=headers, status_code=206 if range_header else 200)

# GET / for health check.
@app.get("/")
def read_root():
    return {"Hello": "World"}

# POST /video to upload a video file.
@app.post("/video/")
async def create_upload_file(file: UploadFile = File(...)):
    # Generate a random UUID for the file name
    file_extension = file.filename.split('.')[-1]
    random_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Define the path where the file will be stored
    file_path = os.path.join(STORAGE_DIR, random_filename)
    
    # Save the file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Return the file size and the URL
    return {"size": os.path.getsize(file_path), "url": random_filename}

# POST /video/{video_path}/search to search for a video frame.
@app.post("/video/{video_path}/search")
def search_video_frame(video_path: str, text: str):
    video_file_path = os.path.join(STORAGE_DIR, video_path)
    
    if not os.path.exists(video_file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Extract frames and their timestamps
    frames, timestamps = extract_frames(video_file_path)

    # Match query to frames
    match_time = match_query_to_frame(frames, timestamps, text)
    
    return {
        "url": f"/media/{video_path}",
        "text": text,
        "time": match_time  # Time in seconds where the first match is found
    }
