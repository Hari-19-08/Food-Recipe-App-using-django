# myrecpies/forms.py

from django import forms
from .models import UserProfile   # instead of Profile



class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile  # Your model for the profile
        fields = ['bio', 'dob', 'profile_pic']  # Fields to include in the form
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
