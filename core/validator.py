from django.core.validators import RegexValidator

email_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9._%+-]+@gmail\.com$",
    message="enter a valid email"
)
username_validator = RegexValidator(
    regex=r'^.{8,}$',
    message='Username must be at least 8 characters long and contain at least one uppercase letter.',
)
password_validator = RegexValidator(
    regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+\-=\[\]{};':'\\|,.<>\/?]).{8,}$",
    message='your password must contain at least one lowercase, uppercase and symbol!'
)
