import { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface ProfileData {
    username: string;
    email: string;
    is_verified: boolean;
    created_at: string;
    role: string;
}

const Profile = () => {
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [error, setError] = useState<string>('');
    const navigate = useNavigate();

    useEffect(() => {
        document.title = 'Profile - DashboardOCR';

        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            navigate('/login');
            return;
        }

        const fetchProfile = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/auth/profile', {
                    headers: {
                        Authorization: `Bearer ${accessToken}`
                    }
                });
                setProfileData(response.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Failed to fetch profile data. Please try again.');
            }
        };

        fetchProfile();
    }, [navigate]);

    if (error) {
        return <div className="text-red-500 text-center mt-4">{error}</div>;
    }

    if (!profileData) {
        return <div className="text-center mt-4">Loading profile...</div>;
    }

    const { username, email, is_verified, created_at, role } = profileData;

    return (
        <div className="flex items-center justify-center  bg-gray-100">
            <div className="bg-white shadow-lg rounded-lg p-8 w-full h-full mx-4 md:mx-8">
                <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">User Profile</h2>
                <div className="space-y-4 text-lg text-gray-700">
                    <p><span className="font-semibold">Username:</span> {username}</p>
                    <p><span className="font-semibold">Email:</span> {email}</p>
                    <p><span className="font-semibold">Verified:</span> {is_verified ? 'Yes' : 'No'}</p>
                    <p><span className="font-semibold">Account Created:</span> {new Date(created_at).toLocaleDateString()}</p>
                    <p><span className="font-semibold">Role:</span> {role}</p>
                </div>
            </div>
        </div>
    );
};

export default Profile;
