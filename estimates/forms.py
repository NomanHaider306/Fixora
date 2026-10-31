from django import forms
from .models import EstimateRequest, EstimateResponse
from services.models import ServiceCategory
from datetime import date


class EstimateRequestForm(forms.ModelForm):
    class Meta:
        model = EstimateRequest
        fields = ['title', 'service_category', 'description', 'job_address', 'preferred_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Electrical rewiring for kitchen remodel'}),
            'service_category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide specific details about the job, problem, materials needed, room dimensions, etc.'}),
            'job_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address, city, zip code'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)
        if provider:
            # Only show categories this provider works in
            prov_cats = provider.categories.all()
            if prov_cats.exists():
                self.fields['service_category'].queryset = prov_cats
            else:
                self.fields['service_category'].queryset = ServiceCategory.objects.filter(is_active=True)

    def clean_preferred_date(self):
        pref_date = self.cleaned_data.get('preferred_date')
        if pref_date and pref_date < date.today():
            raise forms.ValidationError("Preferred date cannot be in the past.")
        return pref_date


class EstimateResponseForm(forms.ModelForm):
    class Meta:
        model = EstimateResponse
        fields = ['estimated_price', 'explanation', 'valid_until']
        widgets = {
            'estimated_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '50.00', 'placeholder': 'e.g. 2500.00'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Explain what is included (e.g. Labor: PKR 1,500, Estimated materials: PKR 1,000. Price may vary upon inspection).'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_estimated_price(self):
        price = self.cleaned_data.get('estimated_price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Estimated price must be greater than 0.")
        return price

