import { useState } from 'react';
import axios from 'axios';

export default function FilePredict() {
  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [outputUrl, setOutputUrl] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileUrl(URL.createObjectURL(selectedFile));
    }
  };

  const handleObjectDetection = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8001/predict/', formData, {
        responseType: 'blob',  // กำหนด responseType เป็น 'blob'
      });

      const url = URL.createObjectURL(response.data);  // สร้าง URL สำหรับ blob
      setOutputUrl(url);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="flex-1 overflow-auto p-6 bg-gray-100">
      <div className="flex">
        <div className="w-1/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">Select File</h3>
            <input
              type="file"
              onChange={handleFileChange}
              accept="video/*, image/*"
              className="mt-4"
            />
            <button
              onClick={handleObjectDetection}
              className="bg-blue-500 text-white px-4 py-2 rounded mt-4"
            >
              Predict
            </button>
            <div className="mt-4">
              {fileUrl && (
                <>
                  <h4 className="font-semibold">Original File:</h4>
                  {file?.type.startsWith('video/') ? (
                    <video width="100%" controls>
                      <source src={fileUrl} type={file.type} />
                      Your browser does not support the video tag.
                    </video>
                  ) : (
                    <img src={fileUrl} alt="Selected" className="w-full h-auto mb-4" />
                  )}
                </>
              )}
              <h4 className="font-semibold">Object Detection Output:</h4>
              {outputUrl && (
                <img src={outputUrl} alt="Object Detection Output" className="w-full h-auto" />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
