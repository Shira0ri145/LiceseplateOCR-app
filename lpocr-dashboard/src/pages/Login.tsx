import { useState } from 'react';
import './Styles/Login.css'; // Import the CSS file for styling
import { Eye, EyeOff } from 'lucide-react';

export default function Login() {
    const [showPassword, setShowPassword] = useState(false);

    const togglePasswordVisibility = () => {
        setShowPassword(prevState => !prevState);
    };
    return (
        <div className="login-wrapper">
            <div className="login-card">
                <h2 className="login-header">Login</h2>
                <form
                    className="login-form"
                    //onSubmit={sumbitForm}
                >
                    <div className="login-form-group">
                        <label htmlFor="username" className="login-form-label">Username:</label>
                        <input
                            type="username"
                            id="username"
                            name="username"
                            className="login-form-input"
                            //value={username}
                            //onChange={inputValue("username")}
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
                                //value={password}
                                //onChange={inputValue("password")}
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
                    <button type="submit" className="login-submit-btn">Login</button>
                </form>
            </div>
        </div>
    );
};