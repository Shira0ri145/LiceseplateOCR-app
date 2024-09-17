import kilmerVideo from '../assets/vdo/kilmer.mp4'; // Import the video file

export default function Content() {
  const data = [
    { type: 'Kilmer', plate: 'ABC123', date: '2023-06-15 14:30:00' },
    { type: 'SUV', plate: 'XYZ789', date: '2023-06-15 15:45:00' },
    { type: 'Truck', plate: 'DEF456', date: '2023-06-15 16:20:00' },
  ];

  // Function to handle video playback at specific times
  const playVideo = () => {
    const video = document.getElementById('videoPlayer') as HTMLVideoElement;
    if (video) {
      const timestamp = 120; // 2 minutes (120 seconds)
      video.currentTime = timestamp;
      video.play();
    }
  };

    // Function to handle video playback at specific times (can be expanded)
    const handlePlayClick = (time: string) => {
      const video = document.getElementById('videoPlayer') as HTMLVideoElement;
      if (video) {
        const timeInSeconds = new Date(time).getSeconds(); // Modify as needed
        video.currentTime = timeInSeconds;
        video.play();
      }
    }

  return (
    <div className="flex-1 overflow-auto p-6 bg-gray-100">
      <div className="flex">
        <div className="w-2/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">License Plate Data</h3>
            <table className="min-w-full mt-4">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Car Type</th>
                  <th className="text-left py-2">License Plate</th>
                  <th className="text-left py-2">Date Timestamp</th>
                  <th className="text-left py-2">Action</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, index) => (
                  <tr key={index} className="border-b">
                    <td className="py-2">{item.type}</td>
                    <td className="py-2">{item.plate}</td>
                    <td className="py-2">{item.date}</td>
                    <td className="py-2">
                      <button
                        onClick={() => handlePlayClick(item.date)}
                        className="bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
                      >
                        Play
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="w-1/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">Video Player</h3>
            <div className="mt-4">
              <div className="w-full h-64 bg-black flex items-center justify-center">
                <video id="videoPlayer" width="100%" height="100%" controls>
                  <source src={kilmerVideo} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
              <div className="mt-4">
                  <button
                    key="Thumbnail"
                    onClick={() => playVideo()}
                    className="bg-gray-300 p-2 rounded hover:bg-gray-400 mt-3 mr-2 mb-2"
                  >Thumbnail
                  </button>
              </div>
              <p className="text-gray-600 mt-2 text-sm">
                Click on a thumbnail or button to play the video at the specified time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
