import { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation, useNavigate } from 'react-router-dom';
import './Styles/Verify.css';

const Verify = () => {
    const [loading, setLoading] = useState(true);
    const [verified, setVerified] = useState(false);
    const [error, setError] = useState('');
    const [countdown, setCountdown] = useState(5);
    const [username, setUsername] = useState('');
    const [message, setMessage] = useState('');
    const [detail, setDetail] = useState('');

    const location = useLocation();
    const navigate = useNavigate();
    
    const getTokenFromURL = () => {
        const params = new URLSearchParams(location.search);
        return params.get('token');
    };

    useEffect(() => {
        document.title = 'File Predict - DashboardOCR';
        const token = getTokenFromURL();

        const verifyEmail = async () => {
            if (token) {
                try {
                    const response = await axios.get(`http://localhost:8000/api/auth/verification?token=${token}`);
                    setMessage(response.data.message);
                    setUsername(response.data.username);
                    setDetail(response.data.detail);
                    setVerified(true);
                    setLoading(false);
                    startCountdown();
                } catch (error: any) {
                    // Capture error message from HTTPException
                    const errorMessage = error.response?.data?.detail || 'Failed to verify email. Please try again.';
                    setError(errorMessage);
                    setLoading(false);
                }
            } else {
                setError('No token provided.');
                setLoading(false);
            }
        };

        verifyEmail();
    }, [location]);

    const startCountdown = () => {
        const interval = setInterval(() => {
            setCountdown(prevCountdown => {
                if (prevCountdown <= 1) {
                    clearInterval(interval);
                    navigate('/login');  // Redirect to login page
                    return 0;
                }
                return prevCountdown - 1;
            });
        }, 1000);
    };

    if (loading) {
        return <div className="verify-wrapper"><p>Loading...</p></div>;
    }

    return (
        <div className="verify-wrapper">
            <div className="verify-card">
                <h2 className="verify-header">Email Verification</h2>
                {verified ? (
                    <>
                        <p className="success-message">{message}</p>
                        <p>Welcome to DashboardOCRapp, Dear. <span className="bold-blue">{username}</span></p>
                        <p>{detail}</p>
                        <p>We will redirect you to the login page in {countdown} seconds...</p>
                    </>
                ) : (
                    <div className="error-message">
                        <p>Error: {error}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Verify;