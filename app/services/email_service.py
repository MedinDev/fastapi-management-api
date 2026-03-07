from typing import Any

class EmailService:
    def __init__(self):
        pass

    async def send_welcome_email(self, email: str) -> None:
        """
        Send a welcome email to the user.
        For now, this is a placeholder that just prints to the console.
        """
        print(f"Sending welcome email to {email}")
