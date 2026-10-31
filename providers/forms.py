from django import forms
from .models import ProviderProfile, PortfolioImage, IdentityDocument
from services.models import ServiceCategory
from django.core.exceptions import ValidationError


class ProviderProfileForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Service Categories"
    )

    class Meta:
        model = ProviderProfile
        fields = [
            'business_name',
            'introduction',
            'skills',
            'experience_years',
            'categories',
            'service_area',
            'city',
            'hourly_rate',
            'starting_price',
            'profile_picture',
            'is_online'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lahore Master Electric Solutions'}),
            'introduction': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell clients about your background, craftsmanship, and work ethic...'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Panel wiring, Inverter/UPS installation, DB dressing, Troubleshooting'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 60}),
            'service_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DHA, Gulberg, Model Town, Johar Town, 20-km radius'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lahore, Karachi, Islamabad'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '50.00', 'min': '0'}),
            'starting_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '100.00', 'min': '0'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'is_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Describe this project (e.g. Master bathroom piping remodel)'}),
        }

    def clean_image(self):
        img = self.cleaned_data.get('image')
        if img:
            if img.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Image file size must not exceed 5MB.")
            ext = img.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                raise ValidationError("Allowed image formats: JPG, JPEG, PNG, WEBP, GIF.")
        return img


class IdentityDocumentForm(forms.ModelForm):
    class Meta:
        model = IdentityDocument
        fields = ['document_type', 'document_file', 'notes']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Any details about this document'}),
        }

    def clean_document_file(self):
        doc = self.cleaned_data.get('document_file')
        if doc:
            if doc.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError("Document file size must not exceed 10MB.")
            ext = doc.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise ValidationError("Allowed document formats: PDF, JPG, PNG.")
        return doc

