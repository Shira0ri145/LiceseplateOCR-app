import { useEffect, useRef, useState } from 'react';
import './Styles/Content.css';

export default function Content() {
  useEffect(() => {
    document.title = 'Home - DashboardOCR';
  }, []);

  const videoRef = useRef<HTMLVideoElement | null>(null); // Reference to the video element for camera
  const predictionRef = useRef<HTMLVideoElement | null>(null); // Reference to the video element for predictions
  const [isCameraActive, setIsCameraActive] = useState(false); // State to track camera status
  const [stream, setStream] = useState<MediaStream | null>(null); // State to store the MediaStream

  // Function to start the camera and prediction
  const handleStartCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current && predictionRef.current) {
        videoRef.current.srcObject = mediaStream; // Set camera stream for Camera
        predictionRef.current.srcObject = mediaStream; // Set the same stream for Prediction
        videoRef.current.play();
        predictionRef.current.play();
        setStream(mediaStream); // Store the stream
        setIsCameraActive(true);
      }
    } catch (error) {
      console.error('Error accessing the camera:', error);
    }
  };

  // Function to stop the camera
  const handleStopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop()); // Stop all tracks
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null; // Clear the video source
    }
    if (predictionRef.current) {
      predictionRef.current.srcObject = null; // Clear the prediction source
    }
    setIsCameraActive(false); // Update camera status
  };

  return (
    <div className="flex-1 overflow-auto p-6 bg-gray-100">
      <div className="flex items-center mb-4">
        {isCameraActive ? (
          <button
            onClick={handleStopCamera}
            className="bg-red-500 text-white ml-5 px-4 py-2 rounded hover:bg-red-600"
          >
            Close Camera
          </button>
        ) : (
          <button
            onClick={handleStartCamera}
            className="bg-blue-500 text-white ml-5 px-4 py-2 rounded hover:bg-blue-600"
          >
            Open Camera
          </button>
        )}
      </div>

      <div className="flex mt-4">
        <div className="w-1/2 p-6"> {/* กล้องอยู่ด้านซ้าย */}
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">Camera</h3>
            <div className="mt-4 video-container">
              <video
                ref={videoRef}
                className="video"
                controls
                autoPlay
              />
            </div>
          </div>
        </div>

        <div className="w-1/2 p-6"> {/* Predict อยู่ด้านขวา */}
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg mt-4 font-semibold">Predict</h3>
            <div className="mt-4 video-container">
              <video
                ref={predictionRef}
                className="video"
                controls
                autoPlay
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
