from django import forms
from .models import ServiceCategory


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'icon_class', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Electrical Services'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe what services fall under this category...'}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bi-lightning-charge, bi-wrench, bi-brush'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

