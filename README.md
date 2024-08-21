# Video GPT

This repository contains a test project to search for frames in a video using Natural Language.

## Installation

### Backend FastAPI

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip3 install "fastapi[standard]" opencv-python-headless torch transformers Pillow
fastapi dev main.py
```

### Frontend React

```bash
cd frontend
npm install
npm run dev
```

## Usage

Open the browser at http://localhost:3000 and upload a video file. Then, you can search for frames using Natural Language.

## License

This project is licensed under the MIT License.
