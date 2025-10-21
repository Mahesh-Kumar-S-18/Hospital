from django import forms
from .models import CustomUser, PatientFile, Patient

class RegisterForm(forms.ModelForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "role"]

class PatientFileUploadForm(forms.ModelForm):
    class Meta:
        model = PatientFile
        fields = ['patient_name', 'patient_id', 'disease', 'file', 'access_email']

class SendFileForm(forms.Form):
    email = forms.EmailField(label="Enter recipient's email")

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        exclude = ['uploaded_by', 'pdf_file', 'otp', 'access_email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make date field user-friendly
        self.fields['date_of_birth'].widget = forms.DateInput(attrs={'type': 'date'})

class SendOTPForm(forms.Form):
    email = forms.EmailField(label="Enter recipient's email")
    patient_id = forms.IntegerField(widget=forms.HiddenInput())