import { useEffect, useState } from 'react';
import axios from 'axios';
import kilmerVideo from '../assets/vdo/kilmer.mp4'; // Import the default video file
import { useNavigate } from 'react-router-dom'; // Import useNavigate for redirecting

export default function FilePredict() {
  useEffect(() => {
    document.title = 'Home - DashboardOCR';
  }, []);

  const [file, setFile] = useState<File | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate(); // Initialize useNavigate

  const data = [
    { type: 'Kilmer', plate: 'ABC123', date: '2023-06-15 14:30:00' },
    { type: 'SUV', plate: 'XYZ789', date: '2023-06-15 15:45:00' },
    { type: 'Truck', plate: 'DEF456', date: '2023-06-15 16:20:00' },
    // Add more data as needed...
  ];

  // Function to handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  // Function to toggle modal visibility
  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
  };

  // Function to filter data based on search query
  const filteredData = data.filter(item =>
    item.plate.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderPreview = () => {
    if (!file) return null;

    const fileURL = URL.createObjectURL(file);

    if (file.type.startsWith('video/')) {
      return (
        <video className="mt-2" width="300" controls>
          <source src={fileURL} type={file.type} />
          Your browser does not support the video tag.
        </video>
      );
    } else if (file.type.startsWith('image/')) {
      return (
        <img
          src={fileURL}
          alt="Uploaded preview"
          className="mt-2"
          width="300"
        />
      );
    }

    return <p>Unsupported file type.</p>;
  };

  const uploadFile = async () => {
    if (!file) return;

    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      navigate('/login'); // Redirect to login if token is not found
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/vehicle/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${accessToken}` // Include the access token here
        },
      });
      console.log('File uploaded successfully:', response.data);
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
                {renderPreview()}
                <p>File Name: {file.name}</p>
                <p>Type: {file.type}</p>
                <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
              </div>
            )}
            <div className="flex justify-end mt-4">
              <button
                onClick={toggleModal}
                className="bg-gray-200 px-3 py-1 rounded hover:bg-gray-300 mr-2"
              >
                Cancel
              </button>
              <button
                onClick={uploadFile} // Call the upload function here
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
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
                    <th className="text-left py-2">Car Type</th>
                    <th className="text-left py-2">License Plate</th>
                    <th className="text-left py-2">Detect Time</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredData.map((item, index) => (
                    <tr key={index} className="border-b">
                      <td className="py-2 text-center">{item.type}</td>
                      <td className="py-2 text-center">{item.plate}</td>
                      <td className="py-2 text-center">{item.date}</td>
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
              <div className="w-full flex items-center justify-center">
                <video id="videoPlayer" width="100%" height="100%" controls>
                  <source src={kilmerVideo} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
            <h3 className="text-lg mt-4 font-semibold">Predict</h3>
            <div className="mt-4">
              <div className="w-full flex items-center justify-center">
                <video id="videoPlayer" width="100%" height="100%" controls>
                  <source src={kilmerVideo} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
