import { useState } from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';
import './Styles/Login.css';
import { Eye, EyeOff } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export default function Login() {
    const [showPassword, setShowPassword] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const togglePasswordVisibility = () => {
        setShowPassword(prevState => !prevState);
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
    
        try {
            const response = await axios.post('http://localhost:8000/api/auth/login', {
                email: username,
                password,
            });
    
            const { access_token, message } = response.data; // ดึง access_token และ message
    
            // Store access_token in localStorage
            localStorage.setItem('access_token', access_token);
    
            // แสดงข้อความสำเร็จโดยใช้ message จาก API
            Swal.fire({
                title: 'Success!',
                text: message, // ใช้ค่าจาก API
                icon: 'success',
                confirmButtonText: 'OK',
            }).then(() => {
                navigate('/'); // Navigate to homepage or any protected route
            });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || 'Failed to login. Please try again.';
            Swal.fire({
                title: 'Error',
                text: errorMessage,
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    };

    return (
        <div className="login-wrapper">
            <div className="login-card">
                <h2 className="login-header">Sign-in</h2>
                <form onSubmit={handleSubmit} className="login-form">
                    <div className="login-form-group">
                        <label htmlFor="username" className="login-form-label">Username:</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            className="login-form-input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="login-form-group">
                        <label htmlFor="password" className="login-form-label">Password:</label>
                        <div className="password-container">
                            <input
                                type={showPassword ? "text" : "password"}
                                id="password"
                                name="password"
                                className="login-form-input"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={togglePasswordVisibility}
                            >
                                {showPassword ? <EyeOff /> : <Eye />}
                            </button>
                        </div>
                    </div>
                    <div className="signup-link">
                        Don't have an account? <Link to="/register">Sign up</Link>
                    </div>
                    <button type="submit" className="login-submit-btn">Sign-in</button>
                </form>
            </div>
        </div>
    );
}