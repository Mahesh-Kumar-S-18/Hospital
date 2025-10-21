from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import random
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas

from django.utils import timezone

from .forms import RegisterForm, PatientFileUploadForm, SendFileForm, PatientForm, SendOTPForm
from .models import CustomUser, PatientFile, Patient

# ---------------- Landing Page ----------------
def landing_view(request):
    return render(request, "landing.html")

# ---------------- Register ----------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Check if email already exists
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered. Please use a different email or login.")
                return render(request, "register.html", {"form": form})
            
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken. Please choose a different username.")
                return render(request, "register.html", {"form": form})
            
            user = form.save(commit=False)

            # Generate OTP
            otp = random.randint(100000, 999999)

            # Save user
            user.set_password(user.generate_password())
            user.otp = otp
            user.is_active = True
            user.is_verified = True
            user.save()

            # Send beautiful registration email with OTP
            html_message = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to Secure Health</title>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                    
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }}
                    
                    .email-container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    }}
                    
                    .header {{
                        background: linear-gradient(135deg, #2c7fb8 0%, #1d5a82 100%);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                        position: relative;
                    }}
                    
                    .header::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        height: 4px;
                        background: linear-gradient(90deg, #7fcdbb, #edf8b1, #2c7fb8);
                    }}
                    
                    .logo {{
                        font-size: 28px;
                        font-weight: 700;
                        margin-bottom: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 10px;
                    }}
                    
                    .logo-icon {{
                        background: rgba(255,255,255,0.2);
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    
                    .welcome-text {{
                        font-size: 16px;
                        opacity: 0.9;
                        margin-top: 10px;
                    }}
                    
                    .content {{
                        padding: 40px 30px;
                        background: #f8fafc;
                    }}
                    
                    .greeting {{
                        font-size: 24px;
                        font-weight: 600;
                        color: #2d3748;
                        margin-bottom: 20px;
                    }}
                    
                    .message {{
                        color: #4a5568;
                        margin-bottom: 30px;
                        font-size: 16px;
                    }}
                    
                    .otp-section {{
                        background: white;
                        border-radius: 15px;
                        padding: 30px;
                        text-align: center;
                        margin: 30px 0;
                        border: 2px dashed #e2e8f0;
                        position: relative;
                    }}
                    
                    .otp-label {{
                        font-size: 14px;
                        color: #718096;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        margin-bottom: 15px;
                        font-weight: 600;
                    }}
                    
                    .otp-code {{
                        font-size: 42px;
                        font-weight: 700;
                        color: #2c7fb8;
                        letter-spacing: 8px;
                        margin: 20px 0;
                        font-family: 'Courier New', monospace;
                        background: linear-gradient(135deg, #2c7fb8, #7fcdbb);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    
                    .otp-note {{
                        font-size: 14px;
                        color: #718096;
                        margin-top: 15px;
                    }}
                    
                    .features {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin: 40px 0;
                    }}
                    
                    .feature {{
                        text-align: center;
                        padding: 20px;
                        background: white;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    }}
                    
                    .feature-icon {{
                        width: 50px;
                        height: 50px;
                        background: linear-gradient(135deg, #2c7fb8, #7fcdbb);
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 15px;
                        color: white;
                        font-size: 20px;
                    }}
                    
                    .feature-title {{
                        font-weight: 600;
                        color: #2d3748;
                        margin-bottom: 8px;
                    }}
                    
                    .feature-desc {{
                        font-size: 14px;
                        color: #718096;
                    }}
                    
                    .security-note {{
                        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
                        border: 1px solid #ffd43b;
                        border-radius: 12px;
                        padding: 20px;
                        margin: 30px 0;
                    }}
                    
                    .security-title {{
                        font-weight: 600;
                        color: #856404;
                        margin-bottom: 10px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    
                    .security-list {{
                        list-style: none;
                        color: #856404;
                    }}
                    
                    .security-list li {{
                        margin-bottom: 8px;
                        padding-left: 20px;
                        position: relative;
                    }}
                    
                    .security-list li::before {{
                        content: '🔒';
                        position: absolute;
                        left: 0;
                    }}
                    
                    .next-steps {{
                        background: white;
                        border-radius: 12px;
                        padding: 25px;
                        margin: 30px 0;
                        border-left: 4px solid #2c7fb8;
                    }}
                    
                    .steps-title {{
                        font-weight: 600;
                        color: #2d3748;
                        margin-bottom: 15px;
                        font-size: 18px;
                    }}
                    
                    .steps-list {{
                        list-style: none;
                        counter-reset: step-counter;
                    }}
                    
                    .steps-list li {{
                        margin-bottom: 15px;
                        padding-left: 40px;
                        position: relative;
                        color: #4a5568;
                    }}
                    
                    .steps-list li::before {{
                        counter-increment: step-counter;
                        content: counter(step-counter);
                        position: absolute;
                        left: 0;
                        top: 0;
                        width: 28px;
                        height: 28px;
                        background: linear-gradient(135deg, #2c7fb8, #7fcdbb);
                        color: white;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 14px;
                        font-weight: 600;
                    }}
                    
                    .footer {{
                        background: #1a202c;
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    
                    .footer-links {{
                        display: flex;
                        justify-content: center;
                        gap: 20px;
                        margin: 20px 0;
                    }}
                    
                    .footer-link {{
                        color: #cbd5e0;
                        text-decoration: none;
                        font-size: 14px;
                    }}
                    
                    .footer-link:hover {{
                        color: white;
                    }}
                    
                    .copyright {{
                        font-size: 12px;
                        color: #718096;
                        margin-top: 20px;
                    }}
                    
                    .support {{
                        background: rgba(255,255,255,0.1);
                        padding: 15px;
                        border-radius: 8px;
                        margin-top: 20px;
                        font-size: 14px;
                    }}
                    
                    @media (max-width: 600px) {{
                        .content {{
                            padding: 30px 20px;
                        }}
                        .otp-code {{
                            font-size: 32px;
                            letter-spacing: 6px;
                        }}
                        .features {{
                            grid-template-columns: 1fr;
                        }}
                        .footer-links {{
                            flex-direction: column;
                            gap: 10px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <!-- Header -->
                    <div class="header">
                        <div class="logo">
                            <div class="logo-icon">
                                ⚕️
                            </div>
                            Secure Health
                        </div>
                        <div class="welcome-text">Your Journey to Secure Healthcare Starts Here</div>
                    </div>
                    
                    <!-- Content -->
                    <div class="content">
                        <div class="greeting">Hello {user.username}!</div>
                        
                        <div class="message">
                            Welcome to Secure Health! We're thrilled to have you on board. Your account has been successfully 
                            registered and you're now part of our secure healthcare ecosystem designed to protect patient privacy 
                            with cutting-edge security.
                        </div>
                        
                        <!-- OTP Section -->
                        <div class="otp-section">
                            <div class="otp-label">Your One-Time Password</div>
                            <div class="otp-code">{otp}</div>
                            <div class="otp-note">
                                Use this OTP to login to your Secure Health account. This code expires after use.
                            </div>
                        </div>
                        
                        <!-- Features Grid -->
                        <div class="features">
                            <div class="feature">
                                <div class="feature-icon">🔒</div>
                                <div class="feature-title">Secure Authentication</div>
                                <div class="feature-desc">Military-grade encryption for all your data</div>
                            </div>
                            <div class="feature">
                                <div class="feature-icon">👥</div>
                                <div class="feature-title">Role-Based Access</div>
                                <div class="feature-desc">Access controls based on your responsibilities</div>
                            </div>
                            <div class="feature">
                                <div class="feature-icon">📊</div>
                                <div class="feature-title">Patient Management</div>
                                <div class="feature-desc">Comprehensive patient record management</div>
                            </div>
                        </div>
                        
                        <!-- Security Notes -->
                        <div class="security-note">
                            <div class="security-title">
                                🛡️ Security First - Important Notes
                            </div>
                            <ul class="security-list">
                                <li>Never share your OTP with anyone</li>
                                <li>Secure Health will never ask for your password</li>
                                <li>Always verify the sender's email address</li>
                                <li>Use secure networks when accessing patient data</li>
                            </ul>
                        </div>
                        
                        <!-- Next Steps -->
                        <div class="next-steps">
                            <div class="steps-title">Ready to Get Started?</div>
                            <ol class="steps-list">
                                <li>Go to the Secure Health login page</li>
                                <li>Enter your username: <strong>{user.username}</strong></li>
                                <li>Use the OTP provided above to access your account</li>
                                <li>Explore your dashboard and set up your profile</li>
                                <li>Start managing healthcare data securely</li>
                            </ol>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="footer">
                        <div class="footer-links">
                            <a href="#" class="footer-link">Privacy Policy</a>
                            <a href="#" class="footer-link">Terms of Service</a>
                            <a href="#" class="footer-link">Help Center</a>
                            <a href="#" class="footer-link">Contact Support</a>
                        </div>
                        
                        <div class="support">
                            Need help? Contact our support team at support@securehealth.com or call +1 (555) 123-HELP
                        </div>
                        
                        <div class="copyright">
                            &copy; 2025 Secure Health. All rights reserved.<br>
                            Protecting Patient Privacy with Advanced Security Solutions
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Send the beautiful email
            send_mail(
                subject="🎉 Welcome to Secure Health - Your OTP for Login",
                message=f"""Hello {user.username},

Welcome to Secure Health!

Your account has been successfully registered.

Your OTP for login: {otp}

Use this OTP to login to your account.

Thank you,
Secure Health Team""",
                html_message=html_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, "🎉 Registration successful! Check your email for OTP to login.")
            return redirect("login")
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, "register.html", {"form": form})

# ---------------- Request new OTP ----------------
def request_otp_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if not username:
            messages.error(request, "Please enter your username.")
            return render(request, "request_otp.html")
        
        try:
            user = CustomUser.objects.get(username=username)
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Send OTP via email with proper formatting
            send_mail(
                "Secure Health - OTP Login Request",
                f"""Hello {user.username},

You requested a new OTP for login.

Your OTP for login: {otp}

Use this OTP to login to your account.

If you didn't request this, please ignore this email.

Thank you,
Secure Health Team""",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your registered email. Please check and login.")
            return redirect("login")
        except CustomUser.DoesNotExist:
            messages.error(request, "Username not found. Please check your username or register.")

    return render(request, "request_otp.html")

# ---------------- Login with OTP ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        otp_input = request.POST.get("otp", "").strip()

        # Validate inputs
        if not username:
            messages.error(request, "Please enter your username.")
            return render(request, "login.html")
        
        if not otp_input:
            messages.error(request, "Please enter the OTP.")
            return render(request, "login.html")

        if not otp_input.isdigit() or len(otp_input) != 6:
            messages.error(request, "OTP must be a 6-digit number.")
            return render(request, "login.html")

        try:
            user = CustomUser.objects.get(username=username)
            if user.otp and str(user.otp) == str(otp_input):
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                
                # Redirect based on role
                if user.role == "admin":
                    return redirect("admin_dashboard")
                elif user.role == "doctor":
                    return redirect('doctor_dashboard')
                elif user.role == "management":
                    return redirect('management_dashboard')
                else:
                    return redirect("dashboard")
            else:
                messages.error(request, "Invalid OTP. Please check and try again.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid username. Please check and try again.")

    return render(request, "login.html")

# ---------------- Logout ----------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("landing")

# ---------------- Dashboards ----------------
@login_required
def dashboard_view(request):
    if request.user.role == "admin":
        return render(request, "admin_dashboard.html", {"role": request.user.role})
    elif request.user.role == "doctor":
        return redirect('doctor_dashboard')
    elif request.user.role == "management":
        return redirect('management_dashboard')
    else:
        return render(request, "dashboard.html", {"role": request.user.role})

# ---------------- Admin Dashboard ----------------
@login_required
def admin_dashboard_view(request):
    if request.user.role != "admin":
        messages.error(request, "Unauthorized access")
        return redirect('dashboard')
    
    # Get counts for dashboard stats
    doctors_count = CustomUser.objects.filter(role="doctor").count()
    management_count = CustomUser.objects.filter(role="management").count()
    patients_count = Patient.objects.count()
    
    # Get lists of doctors and management staff
    doctors = CustomUser.objects.filter(role="doctor")
    management = CustomUser.objects.filter(role="management")
    
    return render(request, "admin_dashboard.html", {
        "role": request.user.role,
        "doctors_count": doctors_count,
        "management_count": management_count,
        "patients_count": patients_count,
        "doctors": doctors,
        "management": management
    })

# ---------------- Doctor Dashboard + Upload ----------------
@login_required
def doctor_dashboard_view(request):
    if request.user.role != 'doctor':
        messages.error(request, "Unauthorized access")
        return redirect('dashboard')

    files = PatientFile.objects.filter(doctor=request.user).order_by('-uploaded_at')

    # Handle file upload
    if request.method == "POST" and 'upload_file' in request.POST:
        form = PatientFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            patient_file = form.save(commit=False)
            patient_file.doctor = request.user
            patient_file.save()
            messages.success(request, "File uploaded successfully.")
            return redirect('doctor_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PatientFileUploadForm()

    # Handle sending OTP
    if request.method == "POST" and 'send_otp' in request.POST:
        file_id = request.POST.get("file_id")
        email = request.POST.get("email", "").strip()
        
        if not email:
            messages.error(request, "Please enter recipient's email address.")
        else:
            try:
                validate_email(email)
                file_obj = get_object_or_404(PatientFile, id=file_id, doctor=request.user)
                otp = file_obj.generate_otp()
                file_obj.access_email = email
                file_obj.save()

                # Send OTP to recipient with proper formatting
                send_mail(
                    'Secure Health - Access Patient File',
                    f"""Hello,

You have been given access to patient medical records.

Patient: {file_obj.patient_name}
File: {file_obj.file.name}

Use this OTP to access the file: {otp}

This OTP is valid for one-time use only.

Thank you,
Secure Health Team""",
                    settings.EMAIL_HOST_USER,
                    [file_obj.access_email],
                    fail_silently=False,
                )
                messages.success(request, f"OTP sent successfully to {file_obj.access_email}.")
            except ValidationError:
                messages.error(request, "Please enter a valid email address.")
            except PatientFile.DoesNotExist:
                messages.error(request, "File not found.")

        return redirect('doctor_dashboard')

    send_form = SendFileForm()

    return render(request, 'doctor_dashboard.html', {
        'form': form,
        'files': files,
        'send_form': send_form
    })

# ---------------- Secure access view ----------------
@login_required
def access_patient_file_view(request, file_id):
    file_obj = get_object_or_404(PatientFile, id=file_id)

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        otp = request.POST.get("otp", "").strip()

        if not email or not otp:
            messages.error(request, "Please enter both email and OTP.")
        elif email == file_obj.access_email and otp == file_obj.otp:
            file_obj.otp = None  # OTP used
            file_obj.save()
            return redirect(file_obj.file.url)
        else:
            messages.error(request, "Invalid email or OTP")

    return render(request, 'access_file.html', {'file': file_obj})

# ---------------- Admin only ----------------
def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.role == "admin",
        login_url='login'
    )(view_func)

@admin_required
def manage_doctors_view(request):
    doctors = CustomUser.objects.filter(role="doctor")
    return render(request, "manage_doctors.html", {"doctors": doctors})

@admin_required
def manage_management_view(request):
    management = CustomUser.objects.filter(role="management")
    return render(request, "manage_management.html", {"management": management})

@admin_required
def remove_user_view(request, user_id):
    if request.method == "POST":
        try:
            user = CustomUser.objects.get(id=user_id)
            # Prevent admin from deleting themselves
            if user.id != request.user.id:
                username = user.username
                user.delete()
                messages.success(request, f"User {username} has been removed successfully.")
            else:
                messages.error(request, "You cannot remove your own account.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
    
    return redirect("admin_dashboard")

# ---------------- Management decorator ----------------
def management_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.role == "management",
        login_url='login'
    )(view_func)

# ---------------- Management Dashboard ----------------
@management_required
def management_dashboard_view(request):
    patients = Patient.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    patient_form = PatientForm()
    send_otp_form = SendOTPForm()

    # Handle new patient entry
    if request.method == "POST":
        if 'upload_patient' in request.POST:
            patient_form = PatientForm(request.POST)
            if patient_form.is_valid():
                patient = patient_form.save(commit=False)
                patient.uploaded_by = request.user
                patient.save()

                # Generate PDF with professional formatting
                buffer = BytesIO()
                p = canvas.Canvas(buffer)
                
                # Set up PDF styling
                p.setFont("Helvetica-Bold", 16)
                p.setFillColorRGB(0.2, 0.4, 0.6)  # Dark blue color
                p.drawString(100, 800, "SECURE HEALTH - PATIENT MEDICAL RECORD")
                
                # Add logo/header line
                p.setStrokeColorRGB(0.2, 0.4, 0.6)
                p.setLineWidth(2)
                p.line(100, 790, 500, 790)
                
                # Patient Information Section
                p.setFont("Helvetica-Bold", 12)
                p.setFillColorRGB(0.3, 0.3, 0.3)
                p.drawString(100, 760, "PATIENT INFORMATION")
                
                p.setFont("Helvetica", 10)
                p.setFillColorRGB(0, 0, 0)
                p.drawString(100, 740, f"Full Name: {patient.full_name}")
                p.drawString(100, 725, f"Date of Birth: {patient.date_of_birth}")
                p.drawString(100, 710, f"Gender: {patient.gender}")
                p.drawString(100, 695, f"National ID: {patient.national_id}")
                p.drawString(100, 680, f"Email: {patient.email}")
                p.drawString(100, 665, f"Phone: {patient.phone}")
                p.drawString(100, 650, f"Address: {patient.address}")
                
                # Contact Information Section
                p.setFont("Helvetica-Bold", 12)
                p.setFillColorRGB(0.3, 0.3, 0.3)
                p.drawString(100, 620, "CONTACT INFORMATION")
                
                p.setFont("Helvetica", 10)
                p.setFillColorRGB(0, 0, 0)
                p.drawString(100, 600, f"Phone: {patient.phone}")
                p.drawString(100, 585, f"Email: {patient.email}")
                p.drawString(100, 570, f"Address: {patient.address}")
                
                # Medical Information Section
                p.setFont("Helvetica-Bold", 12)
                p.setFillColorRGB(0.3, 0.3, 0.3)
                p.drawString(100, 540, "MEDICAL INFORMATION")
                
                p.setFont("Helvetica", 10)
                y_position = 520
                
                # Medical History with text wrapping
                medical_history = patient.medical_history or "Not specified"
                if len(medical_history) > 80:
                    medical_history_lines = [medical_history[i:i+80] for i in range(0, len(medical_history), 80)]
                    p.drawString(100, y_position, "Medical History:")
                    y_position -= 15
                    for line in medical_history_lines[:3]:  # Limit to 3 lines
                        p.drawString(120, y_position, line)
                        y_position -= 15
                    if len(medical_history_lines) > 3:
                        p.drawString(120, y_position, "...")
                        y_position -= 15
                else:
                    p.drawString(100, y_position, f"Medical History: {medical_history}")
                    y_position -= 15
                
                # Diagnosis
                diagnosis = patient.diagnosis or "Not specified"
                if len(diagnosis) > 80:
                    diagnosis_lines = [diagnosis[i:i+80] for i in range(0, len(diagnosis), 80)]
                    p.drawString(100, y_position, "Diagnosis:")
                    y_position -= 15
                    for line in diagnosis_lines[:2]:
                        p.drawString(120, y_position, line)
                        y_position -= 15
                else:
                    p.drawString(100, y_position, f"Diagnosis: {diagnosis}")
                    y_position -= 15
                
                # Lab Results
                lab_results = patient.lab_results or "Not specified"
                p.drawString(100, y_position, f"Lab Results: {lab_results}")
                y_position -= 15
                
                # Imaging Reports
                imaging_reports = patient.imaging_reports or "Not specified"
                p.drawString(100, y_position, f"Imaging Reports: {imaging_reports}")
                y_position -= 15
                
                # Prescriptions
                prescriptions = patient.prescriptions or "Not specified"
                p.drawString(100, y_position, f"Prescriptions: {prescriptions}")
                y_position -= 15
                
                # Immunizations
                immunizations = patient.immunizations or "Not specified"
                p.drawString(100, y_position, f"Immunizations: {immunizations}")
                y_position -= 15
                
                # Financial Information Section
                p.setFont("Helvetica-Bold", 12)
                p.setFillColorRGB(0.3, 0.3, 0.3)
                p.drawString(100, y_position - 20, "FINANCIAL INFORMATION")
                y_position -= 40
                
                p.setFont("Helvetica", 10)
                p.drawString(100, y_position, f"Insurance Details: {patient.insurance_details or 'Not specified'}")
                y_position -= 15
                p.drawString(100, y_position, f"Payment Information: {patient.payment_info or 'Not specified'}")
                y_position -= 15
                p.drawString(100, y_position, f"Bank Account: {patient.bank_account or 'Not specified'}")
                
                # Footer
                p.setFont("Helvetica-Oblique", 8)
                p.setFillColorRGB(0.5, 0.5, 0.5)
                p.drawString(100, 50, "This document contains confidential patient information. Unauthorized access is prohibited.")
                p.drawString(100, 40, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
                p.drawString(100, 30, "Secure Health - Protecting Patient Privacy")
                
                p.showPage()
                p.save()
                pdf_value = buffer.getvalue()
                buffer.close()
                patient.pdf_file.save(f"{patient.full_name.replace(' ', '_')}_medical_record.pdf", ContentFile(pdf_value))

                # Generate OTP
                otp = patient.generate_otp()

                # Send beautiful email to uploader
                html_message = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background: linear-gradient(135deg, #2c7fb8, #1d5a82);
                            color: white;
                            padding: 30px;
                            text-align: center;
                            border-radius: 10px 10px 0 0;
                        }}
                        .content {{
                            background: #f8f9fa;
                            padding: 30px;
                            border: 1px solid #e9ecef;
                        }}
                        .otp-box {{
                            background: #ffffff;
                            border: 2px dashed #2c7fb8;
                            padding: 20px;
                            text-align: center;
                            margin: 20px 0;
                            border-radius: 8px;
                        }}
                        .otp-code {{
                            font-size: 32px;
                            font-weight: bold;
                            color: #2c7fb8;
                            letter-spacing: 5px;
                        }}
                        .footer {{
                            background: #343a40;
                            color: white;
                            padding: 20px;
                            text-align: center;
                            border-radius: 0 0 10px 10px;
                            font-size: 12px;
                        }}
                        .patient-info {{
                            background: white;
                            padding: 20px;
                            border-radius: 8px;
                            margin: 20px 0;
                            border-left: 4px solid #2c7fb8;
                        }}
                        .button {{
                            display: inline-block;
                            background: #2c7fb8;
                            color: white;
                            padding: 12px 30px;
                            text-decoration: none;
                            border-radius: 5px;
                            margin: 10px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Secure Health</h1>
                        <p>Patient Record Successfully Created</p>
                    </div>
                    
                    <div class="content">
                        <h2>Hello {request.user.username},</h2>
                        
                        <p>Your patient medical record has been successfully created and stored securely in our system.</p>
                        
                        <div class="patient-info">
                            <h3>Patient Details:</h3>
                            <p><strong>Name:</strong> {patient.full_name}</p>
                            <p><strong>Date of Birth:</strong> {patient.date_of_birth}</p>
                            <p><strong>Patient ID:</strong> {patient.id}</p>
                            <p><strong>Created:</strong> {timezone.now().strftime('%B %d, %Y at %H:%M')}</p>
                        </div>
                        
                        <div class="otp-box">
                            <h3>Your Access OTP</h3>
                            <p>Use this One-Time Password to access the patient's PDF file:</p>
                            <div class="otp-code">{otp}</div>
                            <p><small>This OTP is valid for one-time use only</small></p>
                        </div>
                        
                        <p><strong>Important Security Notes:</strong></p>
                        <ul>
                            <li>Keep this OTP confidential</li>
                            <li>Do not share via unsecured channels</li>
                            <li>The OTP will expire after use</li>
                            <li>Contact support if you need assistance</li>
                        </ul>
                        
                        <p>You can access the patient record from your management dashboard.</p>
                    </div>
                    
                    <div class="footer">
                        <p>&copy; 2025 Secure Health. All rights reserved.</p>
                        <p>This email contains confidential information. If you received this in error, please delete it.</p>
                    </div>
                </body>
                </html>
                """

                # Send email with HTML content
                send_mail(
                    subject="Secure Health - Patient Record Created Successfully",
                    message=f"""Hello {request.user.username},

Your patient record has been successfully created.

Patient: {patient.full_name}
Date of Birth: {patient.date_of_birth}

Your OTP to access this patient file: {otp}

Use this OTP when you need to access the PDF file.

Thank you,
Secure Health Team""",
                    html_message=html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                messages.success(request, "✅ Patient added successfully! PDF generated and OTP sent to your email.")
                return redirect('management_dashboard')
            else:
                messages.error(request, "❌ Please correct the errors in the form.")

        elif 'send_otp' in request.POST:
            email = request.POST.get("email", "").strip()
            patient_id = request.POST.get("patient_id")
            
            if not email:
                messages.error(request, "❌ Please enter recipient's email address.")
            elif patient_id:
                try:
                    validate_email(email)
                    patient = Patient.objects.get(id=patient_id, uploaded_by=request.user)
                    patient.access_email = email
                    otp = patient.generate_otp()
                    patient.save()

                    # Send beautiful OTP email to recipient
                    html_message = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                line-height: 1.6;
                                color: #333;
                                max-width: 600px;
                                margin: 0 auto;
                                padding: 20px;
                            }}
                            .header {{
                                background: linear-gradient(135deg, #2c7fb8, #1d5a82);
                                color: white;
                                padding: 30px;
                                text-align: center;
                                border-radius: 10px 10px 0 0;
                            }}
                            .content {{
                                background: #f8f9fa;
                                padding: 30px;
                                border: 1px solid #e9ecef;
                            }}
                            .otp-box {{
                                background: #ffffff;
                                border: 2px dashed #2c7fb8;
                                padding: 20px;
                                text-align: center;
                                margin: 20px 0;
                                border-radius: 8px;
                            }}
                            .otp-code {{
                                font-size: 32px;
                                font-weight: bold;
                                color: #2c7fb8;
                                letter-spacing: 5px;
                            }}
                            .footer {{
                                background: #343a40;
                                color: white;
                                padding: 20px;
                                text-align: center;
                                border-radius: 0 0 10px 10px;
                                font-size: 12px;
                            }}
                            .patient-info {{
                                background: white;
                                padding: 20px;
                                border-radius: 8px;
                                margin: 20px 0;
                                border-left: 4px solid #2c7fb8;
                            }}
                            .security-note {{
                                background: #fff3cd;
                                border: 1px solid #ffeaa7;
                                padding: 15px;
                                border-radius: 5px;
                                margin: 15px 0;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>Secure Health</h1>
                            <p>Access to Patient Medical Records</p>
                        </div>
                        
                        <div class="content">
                            <h2>Secure Access Granted</h2>
                            
                            <p>You have been granted temporary access to patient medical records through Secure Health.</p>
                            
                            <div class="patient-info">
                                <h3>Patient Information:</h3>
                                <p><strong>Name:</strong> {patient.full_name}</p>
                                <p><strong>Date of Birth:</strong> {patient.date_of_birth}</p>
                                <p><strong>Authorized By:</strong> {request.user.username}</p>
                                <p><strong>Access Provided:</strong> {timezone.now().strftime('%B %d, %Y at %H:%M')}</p>
                            </div>
                            
                            <div class="otp-box">
                                <h3>Your One-Time Access Code</h3>
                                <p>Use this code to securely access the patient file:</p>
                                <div class="otp-code">{otp}</div>
                                <p><small>Valid for one-time use only • Expires after use</small></p>
                            </div>
                            
                            <div class="security-note">
                                <h4>🔒 Security Instructions:</h4>
                                <ul>
                                    <li>This OTP provides access to sensitive medical information</li>
                                    <li>Do not share this code with anyone</li>
                                    <li>Access the file only through official Secure Health channels</li>
                                    <li>This access is logged for security purposes</li>
                                </ul>
                            </div>
                            
                            <p><strong>Next Steps:</strong></p>
                            <ol>
                                <li>Go to the Secure Health portal</li>
                                <li>Navigate to the patient file access section</li>
                                <li>Enter your email and the OTP above</li>
                                <li>Access will be granted immediately</li>
                            </ol>
                        </div>
                        
                        <div class="footer">
                            <p>&copy; 2025 Secure Health. All rights reserved.</p>
                            <p>Confidentiality Notice: This email contains protected health information.</p>
                        </div>
                    </body>
                    </html>
                    """

                    # Send email with HTML content
                    send_mail(
                        subject="Secure Health - Access to Patient Medical Records",
                        message=f"""Hello,

You have been granted access to patient medical records.

Patient: {patient.full_name}
Date of Birth: {patient.date_of_birth}

Use this OTP to access the patient file: {otp}

This OTP is valid for one-time use only.

Thank you,
Secure Health Team""",
                        html_message=html_message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[patient.access_email],
                        fail_silently=False,
                    )
                    messages.success(request, f"✅ OTP sent successfully to {patient.access_email}")
                except ValidationError:
                    messages.error(request, "❌ Please enter a valid email address.")
                except Patient.DoesNotExist:
                    messages.error(request, "❌ Patient not found.")
            else:
                messages.error(request, "❌ Invalid patient selection.")

            return redirect('management_dashboard')

    return render(request, 'management_dashboard.html', {
        'patient_form': patient_form,
        'patients': patients,
        'send_otp_form': send_otp_form,
        'patients_count': patients.count(),
        'patients_with_pdf': patients.exclude(pdf_file=''),
        'otp_sent_count': patients.filter(access_email__isnull=False).count(),
    })
# ---------------- Secure access to patient PDF ----------------
@login_required
def access_patient_pdf_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        otp = request.POST.get('otp', '').strip()

        if not email or not otp:
            messages.error(request, "Please enter both email and OTP.")
        elif ((email == patient.uploaded_by.email or email == patient.access_email) and otp == patient.otp):
            patient.otp = None
            patient.save()
            return redirect(patient.pdf_file.url)
        else:
            messages.error(request, "Invalid email or OTP")

    return render(request, 'access_patient_pdf.html', {'patient': patient})