import { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Define the CroppedImage interface
interface CroppedImage {
  id: string;
  crop_class_name: string;
  license_plate: string | null;
  crop_timestamp: string | null;
  crop_image_url: string; // Include crop_image_url in the interface
}

export default function FilePredict() {
  useEffect(() => {
    document.title = 'Home - DashboardOCR';
  }, []);

  const [file, setFile] = useState<File | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [originalFileUrl, setOriginalFileUrl] = useState('');
  const [predictFileUrl, setPredictFileUrl] = useState('');
  const [uploadType, setUploadType] = useState('');
  const [croppedImages, setCroppedImages] = useState<CroppedImage[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null); // State for the pop-up image
  const navigate = useNavigate();

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
  };

  const handleImageClick = (url: string) => {
    setSelectedImage(url);
  };

  const closeImageModal = () => {
    setSelectedImage(null);
  };

  const uploadFile = async () => {
    if (!file) return;

    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      navigate('/login');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/vehicle/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${accessToken}`,
        },
      });

      setOriginalFileUrl(response.data.upload_url);
      setPredictFileUrl(response.data.detect_url);
      setUploadType(response.data.upload_type);
      setCroppedImages(response.data.cropped_images || []);

      toggleModal(); // Close modal after upload
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="flex-1 overflow-auto p-6 bg-gray-100">
      <div className="flex items-center mb-4">
        <button
          onClick={toggleModal}
          className="bg-blue-500 text-white ml-5 px-4 py-2 rounded hover:bg-blue-600"
        >
          Upload File
        </button>
        <input
          type="text"
          placeholder="Search License Plate"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="border border-gray-300 rounded-md p-2 ml-4"
        />
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-20">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-lg font-semibold mb-4">Upload File</h2>
            <input
              type="file"
              onChange={handleFileUpload}
              className="border border-gray-300 rounded-md p-2 w-full"
            />
            {file && (
              <div className="mt-4">
                <h3 className="font-semibold">Preview:</h3>
                <img src={URL.createObjectURL(file)} alt="Uploaded preview" width="300" />
                <p>File Name: {file.name}</p>
                <p>Type: {file.type}</p>
                <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
              </div>
            )}
            <div className="flex justify-end mt-4">
              <button onClick={toggleModal} className="bg-gray-200 px-3 py-1 rounded hover:bg-gray-300 mr-2">
                Cancel
              </button>
              <button onClick={uploadFile} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                Upload
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex mt-4">
        <div className="w-2/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">License Plate Data</h3>
            <div className="max-h-96 overflow-y-auto mt-4">
            <table className="min-w-full">
              <thead className="bg-gray-100 sticky top-0 z-10">
                <tr className="border-b">
                  <th className="text-center py-2">Detect</th>
                  <th className="text-center py-2">Car Type</th>
                  <th className="text-center py-2">License Plate</th>
                  <th className="text-center py-2">Detect Time</th>
                </tr>
              </thead>
              <tbody className="bg-gray-100">
                {croppedImages.map((image) => (
                  <tr key={image.id} className="border-b">
                    <td className="py-2 text-center">
                      <div className="flex justify-center">
                        <img
                          src={image.crop_image_url}
                          alt="Cropped"
                          className="w-16 h-16 cursor-pointer"
                          onClick={() => handleImageClick(image.crop_image_url)}
                        />
                      </div>
                    </td>
                    <td className="py-2 text-center">{image.crop_class_name}</td>
                    <td className="py-2 text-center">{image.license_plate || 'N/A'}</td>
                    <td className="py-2 text-center">{image.crop_timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            </div>
          </div>
        </div>

        <div className="w-1/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">Original file</h3>
            <div className="mt-4">
              <img src={originalFileUrl} alt="Original file preview" />
            </div>
            <h3 className="text-lg mt-4 font-semibold">Predict</h3>
            <div className="mt-4">
              <img src={predictFileUrl} alt="Predicted file preview" />
            </div>
          </div>
        </div>
      </div>

      {selectedImage && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-20">
          <div className="relative p-4 bg-white rounded-lg shadow-md max-w-sm">
            <img
              src={selectedImage}
              alt="Large preview"
              className="max-w-xs max-h-xs object-contain"
            />
            <button
              onClick={closeImageModal}
              className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
            >
              Close
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
