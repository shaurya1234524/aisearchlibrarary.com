"""
Email verification utilities for user registration
"""
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()


def send_verification_email(user, request):
    """
    Send verification email to the user
    """
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build verification URL
        verification_url = request.build_absolute_uri(
            reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
        )
        
        subject = 'Verify Your Latest Ai Tools Account'
        message = f"""
Hello {user.username},

Thank you for signing up with Latest Ai Tools! To complete your registration, 
please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
The Latest Ai Tools Team
        """
        
        html_message = f"""
<html>
    <body style="font-family: Poppins, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #1a2a6c;">Welcome to Latest Ai Tools!</h2>
            <p>Hi <strong>{user.username}</strong>,</p>
            <p>Thank you for signing up! To complete your registration and access all features, 
            please verify your email address by clicking the button below:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background-color: #e94560; color: white; 
                padding: 12px 30px; text-decoration: none; border-radius: 8px; 
                display: inline-block; font-weight: 600;">Verify Email Address</a>
            </div>
            <p style="color: #666; font-size: 12px;">
                Or copy and paste this link in your browser:<br>
                <a href="{verification_url}" style="color: #e94560;">{verification_url}</a>
            </p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This link will expire in 24 hours. If you didn't create this account, 
                please ignore this email.
            </p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="color: #999; font-size: 12px; text-align: center;">
                © 2025 Latest Ai Tools. All rights reserved.
            </p>
        </div>
    </body>
</html>
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False


def verify_email_token(uidb64, token):
    """
    Verify the token and return the user if valid
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        return user
    return None
