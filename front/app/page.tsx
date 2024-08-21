"use client";

import React from "react";

const VIDEO_API = "http://127.0.0.1:8000";

export default function Home() {
  const [videoURL, setVideoURL] = React.useState<string | null>(null);
  const [searchText, setSearchText] = React.useState<string>("");

  const inputRef = React.useRef<HTMLInputElement>(null);
  const videoRef = React.useRef<HTMLVideoElement>(null);

  const handleUpload = async (videoUpload: File | undefined) => {
    console.log(videoUpload);
    if (!videoUpload) return;

    const formData = new FormData();
    formData.append("file", videoUpload);

    const response = await fetch(`${VIDEO_API}/video/`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const { url } = await response.json();
      setVideoURL(url);
    } else {
      // TODO: Handle error and show message
      alert("Error uploading video");
    }
  }

  const handleSearch = async () => {
    if (searchText === "") return;

    const url = `${VIDEO_API}/video/${videoURL}/search?text=${encodeURIComponent(searchText)}`;

    const response = await fetch(url, {
      method: "POST",
    });

    if (response.ok) {
      const { time } = await response.json();
      console.log("Time found:", time);

      if (time) {
        console.log(videoRef.current!.currentTime)
        videoRef.current!.currentTime = time;
      } else {
        alert("Text not found in video");
      }
    } else {
      console.error('Search failed:', response.statusText);
      return;
    }
  };

  console.log("videoURL", videoURL);

  return (
    <main className="flex h-screen flex-col items-center justify-between">
      <div className="z-10 w-full max-w-5xl items-center justify-between text-sm lg:flex">
        <p className="fixed text-2xl font-bold left-0 top-0 flex w-full justify-center pb-6 pt-8 lg:static lg:w-auto">
          VideoGPT
        </p>
        <div className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center lg:static lg:size-auto">
          <a
            className="pointer-events-none flex place-items-center gap-2 p-8 lg:pointer-events-auto lg:p-0"
            href="https://www.linkedin.com/in/paupenin/"
            target="_blank"
            rel="noopener noreferrer"
          >
            By Pau Penin
          </a>
        </div>
      </div>

      <div className="flex flex-col items-center justify-center w-full h-full gap-4 grow max-h-screen">
        <button className="text-black bg-white rounded px-4 py-2" onClick={() => inputRef.current!.click()}>
          Upload video
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={(e) => handleUpload(e.target.files?.[0])}
        />

        {videoURL && (
          <>
            <div className="flex max-w-xl">
              <input
                type="text"
                placeholder="Use this text to search in the video"
                className="w-full p-2 rounded-l"
                value={searchText}
                onChange={(e) => {console.log(e.target.value); setSearchText(e.target.value)}}
              />
              <button className="text-black bg-slate-100 rounded-r px-4 py-2" onClick={handleSearch}>
                Search
              </button>
            </div>
            <video
              style={{ maxHeight: "calc(100vh - 250px)" }}
              controls
              src={`${VIDEO_API}/media/${videoURL}`}
              ref={videoRef}
            />
          </>
        )}
      </div>
    </main>
  );
}
