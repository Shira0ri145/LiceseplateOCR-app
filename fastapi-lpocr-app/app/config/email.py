import os
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from app.config.settings import get_settings


settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="DashboardOCR",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)

fm = FastMail(config=conf)

async def send_email(recipients: list, subject: str, template: dict):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=template,
        subtype=MessageType.html
    )
    # return message
    await fm.send_message(message=message)

    
'''
async def send_test_email():
    recipients = ["fejom65362@hraifi.com"]

    # print(settings.MAIL_USERNAME)
    # print(settings.MAIL_PASSWORD)
    # print(settings.MAIL_FROM)
    # print(settings.MAIL_PORT)
    # print(settings.MAIL_SERVER)


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
                    href="http://localhost:8000/auth/testmail">
                    Verify your email
                    </a>
                    <p>Please kindly ignore this email if you did not register for DashboardOCR-app and nothing will happen. Thank you.</p>
                </div>
            </body>
        </html>
    """

    
    message = MessageSchema(
        subject="Test Email",
        recipients=recipients,  # ใส่ recipients ที่ต้องการทดสอบ
        body= verify_template,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    '''