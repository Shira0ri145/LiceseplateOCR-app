import { useEffect, useState } from 'react';
import axios from 'axios';

// สร้าง interface สำหรับข้อมูลโปรไฟล์
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

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/auth/profile', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}` // เปลี่ยนเป็น 'access_token' เพื่อให้ตรงกับที่เก็บใน localStorage
                    }
                });
                setProfileData(response.data);
            } catch (err: any) {
                if (err.response && err.response.data && err.response.data.detail) {
                    setError(err.response.data.detail);
                } else {
                    setError('Failed to fetch profile data. Please try again.');
                }
            }
        };

        fetchProfile();
    }, []);

    if (error) {
        return <div className="text-red-500 text-center mt-4">{error}</div>;
    }

    if (!profileData) {
        return <div className="text-center mt-4">Loading profile...</div>;
    }

    // แยกตัวแปรจาก profileData
    const { username, email, is_verified, created_at, role } = profileData;

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white shadow-md rounded-lg p-6 w-full max-w-md">
                <h2 className="text-xl font-semibold mb-4 text-center">User Profile</h2>
                <p className="mb-2"><strong>Username:</strong> {username}</p>
                <p className="mb-2"><strong>Email:</strong> {email}</p>
                <p className="mb-2"><strong>Verified:</strong> {is_verified ? 'Yes' : 'No'}</p>
                <p className="mb-2"><strong>Account Created:</strong> {new Date(created_at).toLocaleDateString()}</p>
                <p className="mb-2"><strong>Role:</strong> {role}</p>
            </div>
        </div>
    );
};

export default Profile;