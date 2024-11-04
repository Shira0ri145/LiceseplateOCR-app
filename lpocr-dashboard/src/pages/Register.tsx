import { useState } from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';
import './Styles/Register.css';
import { Eye, EyeOff, Check, X } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export default function Register() {
    const [showPassword, setShowPassword] = useState(false);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [passwordValidations, setPasswordValidations] = useState({
        minLength: false,
        uppercaseLowercase: false,
        number: false,
        specialChar: false,
    });
    const navigate = useNavigate();

    const togglePasswordVisibility = () => {
        setShowPassword(prevState => !prevState);
    };

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const input = e.target.value;
        setPassword(input);

        setPasswordValidations({
            minLength: input.length >= 8,
            uppercaseLowercase: /[A-Z]/.test(input) && /[a-z]/.test(input),
            number: /\d/.test(input),
            specialChar: /[@#$%=:?.\/|~>]/.test(input),
        });
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        const confirmResult = await Swal.fire({
            title: 'Are you sure?',
            text: "Do you want to create a new account?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, create it!',
            cancelButtonText: 'No, cancel!',
        });

        if (!confirmResult.isConfirmed) return;

        try {
            const response = await axios.post('http://localhost:8000/api/auth/signup', {
                username,
                email,
                password,
            });

            Swal.fire({
                title: 'Success!',
                text: response.data.message,
                icon: 'success',
                confirmButtonText: 'OK',
            }).then(() => {
                navigate('/login');
            });
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || 'Failed to register. Please try again.';
            Swal.fire({
                title: 'Error',
                text: errorMessage,
                icon: 'error',
                confirmButtonText: 'OK',
            });
        }
    };

    return (
        <div className="register-wrapper">
            <div className="register-card">
                <h2 className="register-header">Register</h2>
                <form onSubmit={handleSubmit} className="register-form">
                    <div className="register-form-group">
                        <label htmlFor="username" className="register-form-label">Username:</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            className="register-form-input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="register-form-group">
                        <label htmlFor="email" className="register-form-label">Email:</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            className="register-form-input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="register-form-group">
                        <label htmlFor="password" className="register-form-label">Password:</label>
                        <div className="password-container">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                name="password"
                                className="register-form-input"
                                value={password}
                                onChange={handlePasswordChange}
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
                        <ul className="password-requirements">
                            <li>
                                {passwordValidations.minLength ? <Check color="green" /> : <X color="red" />} 
                                At least 8 characters long
                            </li>
                            <li>
                                {passwordValidations.uppercaseLowercase ? <Check color="green" /> : <X color="red" />} 
                                Contains uppercase and lowercase letters
                            </li>
                            <li>
                                {passwordValidations.number ? <Check color="green" /> : <X color="red" />} 
                                Contains a number
                            </li>
                            <li>
                                {passwordValidations.specialChar ? <Check color="green" /> : <X color="red" />} 
                                Contains a special character (@, #, $, etc.)
                            </li>
                        </ul>
                    </div>
                    <div className="signin-link">
                        Already have an account? <Link to="/login">Sign in</Link>
                    </div>
                    <button type="submit" className="register-submit-btn">Register</button>
                </form>
            </div>
        </div>
    );
}