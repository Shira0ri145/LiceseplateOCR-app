import { useState } from 'react';

export default function FilePredict() {
  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);

  const data = [
    { type: 'Kilmer', plate: 'ABC123', date: '2023-06-15 14:30:00' },
    { type: 'SUV', plate: 'XYZ789', date: '2023-06-15 15:45:00' },
    { type: 'Truck', plate: 'DEF456', date: '2023-06-15 16:20:00' },
  ];

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileUrl(URL.createObjectURL(selectedFile)); // สร้าง URL สำหรับการแสดงผล
    }
  };

  // คอมเมนต์ฟังก์ชันสำหรับ Object Detection Output ไว้ก่อน
  /*
  const handleObjectDetection = () => {
    // ฟังก์ชันสำหรับการเรียก API เพื่อทำ Object Detection
    // จะส่ง `file` ไปยัง FastAPI และรับภาพผลลัพธ์กลับมา
  };
  */

  return (
    <div className="flex-1 overflow-auto p-6 bg-gray-100">
      <div className="flex">
        <div className="w-1/3 p-6">
          <div className="bg-white shadow-md rounded-lg p-4">
            <h3 className="text-lg font-semibold">Select File</h3>
            <input
              type="file"
              onChange={handleFileChange}
              accept="video/*, image/*" // รองรับไฟล์รูปภาพและวิดีโอ
              className="mt-4"
            />
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
                  {/* สถานที่สำหรับแสดง Object Detection Output */}
                  <h4 className="font-semibold">Object Detection Output:</h4>
                  {file?.type.startsWith('video/') ? (
                    <video width="100%" controls>
                      <source src={fileUrl} type={file.type} />
                      Your browser does not support the video tag.
                    </video>
                  ) : (
                    <img src={fileUrl} alt="Object Detection Output" className="w-full h-auto" />
                  )}
                  {/* Futurue will show src ของรูปที่สองนี้by result from yolo Object Detection */}
                </>
              )}
            </div>
          </div>
        </div>

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
                        onClick={() => { /* handlePlayClick(item.date) */ }}
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
      </div>
    </div>
  );
}
