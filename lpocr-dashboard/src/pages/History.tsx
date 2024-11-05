import { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './Styles/History.css';

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
    const [error, setError] = useState<string>(''); 
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUploads = async () => {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                navigate('/login');
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
    }, [navigate]);

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
                    <Link to={`/history/${upload.id}`} key={upload.id} className="upload-item-link">
                        <div className="upload-item">
                            <span>{upload.upload_name}</span>
                            <span>{upload.upload_type}</span>
                            <span>{new Date(upload.created_at).toLocaleString()}</span>
                            
                            {/* Display video or image with square styling */}
                            {upload.upload_type === "video" ? (
                                <video controls className="upload-thumbnail" src={upload.upload_url} />
                            ) : (
                                <img src={upload.upload_url} alt={upload.upload_name} className="upload-thumbnail" />
                            )}
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default History;
