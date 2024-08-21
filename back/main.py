from typing import Union

from fastapi import FastAPI, File

app = FastAPI()


# GET / for health check.
@app.get("/")
def read_root():
    return {"Hello": "World"}

# POST /video to upload a video file.
@app.post("/video/")
def create_upload_file(file: bytes = File(...)):
    return {"file_size": len(file)}

# POST /video/{video_id}/search to search for a video frame.
@app.post("/video/{video_id}/search")
def search_video_frame(video_id: str, text: str):
    return {"video_id": video_id, "text": text}
