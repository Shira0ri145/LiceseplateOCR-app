import jwt
from app.config.settings import get_settings
from app.models.user import Users
from app.config.email import send_email


settings = get_settings()


async def send_account_verification_email(email : list ,user: Users):
    data = {
        "id" : user.id,
        "name": user.username,
    }

    subject = "DashboardOCR Account Verification Email"

    token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')

    # fortest
    # href="http://localhost:8000/api/auth/verification/?token={token}">
    # forclient href="http://localhost:5173/verify/?token={token}"
    verify_template = f"""
        <!DOCTYPE html>
        <html>
            <head>
            </head>
            <body>
                <div style="display: flex; align-items: center; justify-content: center; flex-direction: column">
                    <h3>Account Verification</h3>
                    <br>
                    <p>Please click on the button below to verify your account</p>
                    <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem;
                    text-decoration: none; background: #0275d8; color: white;"
                    href="http://localhost:5173/verify/?token={token}">
                    Verify your email
                    </a>
                    <p>Please kindly ignore this email if you did not register for DashboardOCR-app and nothing will happen. Thank you.</p>
                </div>
            </body>
        </html>
    """

    await send_email(
        recipients=email,
        subject=subject,
        template=verify_template
    )

async def send_password_reset_email(email : list ,user: Users):
    data = {
        "id" : user.id,
        "name": user.username,
    }

    subject = "Reset Your Password"

    token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')
    
    link = f"http://localhost:8000/auth/password-reset-confirm/?token={token}"

    reset_message= f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    await send_email(
        recipients=email,
        subject=subject,
        template=reset_message
    )

