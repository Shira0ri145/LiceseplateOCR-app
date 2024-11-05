import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom'; // Import useParams to get URL parameters
import axios from 'axios'; // Import axios for making API requests

interface FileData {
  upload_url: string;
  obj_detect_url: string;
  upload_type: 'image' | 'video';
  cropped_images: CroppedImage[]; // Add the cropped_images array
}

interface CroppedImage {
  upload_id: number;
  id: number;
  crop_timestamp: number;
  crop_class_name: string;
  crop_image_url: string;
  license_plate: string;
  created_at: string;
  modified_at: string | null;
}

export default function UploadHistory() {
  const { id } = useParams<{ id: string }>(); // Get the ID from the URL parameters

  useEffect(() => {
    document.title = 'Home - DashboardOCR';
    fetchUploadData(); // Call the fetch function
  }, [id]); // Add id as a dependency to refetch if it changes

  const [fileData, setFileData] = useState<FileData | null>(null); // Update the type here
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null); // State for selected image for popup
  const [showPopup, setShowPopup] = useState(false); // State for popup visibility

  const fetchUploadData = async () => {
    if (id) {
      try {
        const response = await axios.get(`http://localhost:8000/api/vehicle/${id}`);
        setFileData(response.data); // Axios will automatically parse the data
      } catch (error) {
        console.error('Error fetching upload data:', error);
        // Handle error here if needed
      }
    }
  };

  const renderPreview = (url: string, type: string) => {
    if (type === 'image') {
      return (
        <img src={url} alt="Uploaded preview" className="mt-2" width="300" />
      );
    } else if (type === 'video') {
      return (
        <video className="mt-2" width="300" controls>
          <source src={url} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      );
    }
    return <p>Unsupported file type.</p>;
  };

  const openPopup = (url: string) => {
    setSelectedImage(url);
    setShowPopup(true);
  };

  const closePopup = () => {
    setShowPopup(false);
    setSelectedImage(null);
  };


  return (
    <div className="flex-1 overflow-auto p-1 bg-gray-100">
      <div className="flex mt-4">
        <div className="w-2/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">License Plate Data</h3>
              <input
                type="text"
                placeholder="Search License Plate"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="border border-gray-300 rounded-md p-2 ml-4"
              />
            </div>
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

                <tbody>
                  {fileData && fileData.cropped_images
                    .filter((image) => {
                      const plate = image.license_plate.toLowerCase();
                      return plate.includes(searchQuery.toLowerCase());
                    })
                    .map((image) => (
                      <tr key={image.id} className="border-b">
                        <td className="py-2 flex justify-center">
                          <img
                            src={image.crop_image_url}
                            alt="Cropped"
                            className="w-16 h-16 cursor-pointer"
                            onClick={() => openPopup(image.crop_image_url)}
                          />
                        </td>
                        <td className="py-2 text-center">{image.crop_class_name}</td>
                        <td className="py-2 text-center">{image.license_plate || 'N/A'}</td>
                        <td className="py-2 text-center">{image.crop_timestamp.toFixed(2)}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
  
        <div className="w-1/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold text-center">Original file</h3>
            <div className="mt-4 flex justify-center">
              {fileData && renderPreview(fileData.upload_url, fileData.upload_type)}
            </div>
            <h3 className="text-lg mt-4 font-semibold text-center">Predict</h3>
            <div className="mt-4 flex justify-center">
              {fileData && renderPreview(fileData.obj_detect_url, fileData.upload_type)}
            </div>
          </div>
        </div>
      </div>
  
      {showPopup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded">
            <img src={selectedImage!} alt="Cropped" className="max-w-full max-h-[80vh]" />
            <button
              onClick={closePopup}
              className="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
  
}
