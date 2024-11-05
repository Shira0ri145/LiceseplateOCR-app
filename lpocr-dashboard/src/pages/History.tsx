import { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Styles/History.css'; // CSS file for styling

interface Upload {
    id: number;
    user_id: number;
    upload_name: string;
    upload_url: string;
    upload_type: string;
    created_at: string;
}

const History = () => {
    const [uploads, setUploads] = useState<Upload[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>(''); // State for error messages
    const navigate = useNavigate(); // To programmatically navigate

    useEffect(() => {
        const fetchUploads = async () => {
            // Check if user is logged in
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                navigate('/login'); // Redirect to login if not authenticated
                return;
            }

            try {
                const response = await axios.get('http://localhost:8000/api/vehicle/user/uploads', {
                    headers: {
                        Authorization: `Bearer ${accessToken}`
                    }
                });
                
                setUploads(response.data);
            } catch (err: any) {
                if (err.response && err.response.data && err.response.data.detail) {
                    setError(err.response.data.detail);
                } else {
                    setError('Failed to fetch uploads. Please try again.');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchUploads();
    }, [navigate]); // Add navigate to the dependency array

    if (loading) {
        return <div className="loading">Loading uploads...</div>;
    }

    if (error) {
        return <div className="text-red-500 text-center mt-4">{error}</div>;
    }

    if (uploads.length === 0) {
        return <div className="empty-state">No uploads found for this user.</div>;
    }

    return (
        <div className="history-container">
            <h1>User Upload History</h1>
            <div className="upload-list">
                {uploads.map((upload) => (
                    <div key={upload.id} className="upload-item">
                        <span>{upload.upload_name} </span>
                        <span>{upload.upload_type} </span>
                        <span>{new Date(upload.created_at).toLocaleString()}</span>
                        
                        {/* Display video or image */}
                        {upload.upload_type === "video" ? (
                            <video controls width="200" src={upload.upload_url} />
                        ) : (
                            <img src={upload.upload_url} alt={upload.upload_name} style={{ width: '200px', height: 'auto' }} />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default History;
