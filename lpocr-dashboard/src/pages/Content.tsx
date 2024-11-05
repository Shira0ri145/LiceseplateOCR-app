import React, { useEffect, useRef, useState } from 'react';
import './Styles/Content.css'; // Import styles

const YOLOv8Detection: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null); // Reference to the video element for camera
  const outputRef = useRef<HTMLImageElement | null>(null); // Reference to the image element for predictions
  const [isCameraActive, setIsCameraActive] = useState(false); // State to track camera status
  const [stream, setStream] = useState<MediaStream | null>(null); // State to store the MediaStream
  const [intervalId, setIntervalId] = useState<number | null>(null); // Interval ID for frame capture

  useEffect(() => {
    document.title = 'Real-Time YOLOv8 Detection'; // Update document title

    return () => {
      // Cleanup on component unmount
      stopCamera();
    };
  }, []);

  // Function to start the camera and prediction
  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream; // Set camera stream
        videoRef.current.play(); // Play video
        setStream(mediaStream); // Store the stream
        setIsCameraActive(true);

        // Start sending frames to FastAPI for YOLOv8 detection
        const id = setInterval(() => {
          captureAndPredict();
        }, 100);
        setIntervalId(id);
      }
    } catch (error) {
      console.error('Error accessing the camera:', error);
    }
  };

  // Function to stop the camera
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop()); // Stop all tracks
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null; // Clear the video source
    }
    setIsCameraActive(false); // Update camera status
    if (intervalId) {
      clearInterval(intervalId); // Clear interval
    }
  };

  // Function to capture frame and send for prediction
  const captureAndPredict = async () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

      const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg'));

      if (blob) {
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');

        const response = await fetch('http://localhost:8000/api/webcam/predict-frame', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const detectedBlob = await response.blob();
          outputRef.current!.src = URL.createObjectURL(detectedBlob);
        } else {
          console.error('Failed to get prediction');
        }
      }
    }
  };

  return (
    <div className="flex-1 overflow-auto p-6 bg-gray-100">
      <div className="flex items-center mb-4">
        {isCameraActive ? (
          <button
            onClick={stopCamera}
            className="bg-red-500 text-white ml-5 px-4 py-2 rounded hover:bg-red-600"
          >
            Close Camera
          </button>
        ) : (
          <button
            onClick={startCamera}
            className="bg-blue-500 text-white ml-5 px-4 py-2 rounded hover:bg-blue-600"
          >
            Open Camera
          </button>
        )}
      </div>

      <div className="flex mt-4">
        <div className="w-1/2 p-6"> {/* Camera on the left */}
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">Camera</h3>
            <div className="mt-4 video-container">
              <video
                ref={videoRef}
                className="video"
                autoPlay
                muted
              />
            </div>
          </div>
        </div>

        <div className="w-1/2 p-6"> {/* Prediction on the right */}
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg mt-4 font-semibold">Predicted Frame</h3>
            <div className="mt-4 video-container">
              <img
                ref={outputRef}
                className="video"
                alt="Detected Frame"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default YOLOv8Detection;
