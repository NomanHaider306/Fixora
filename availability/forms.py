from django import forms
from .models import WeeklySchedule, BlockedDate
from django.core.exceptions import ValidationError
from datetime import date


class WeeklyScheduleForm(forms.ModelForm):
    class Meta:
        model = WeeklySchedule
        fields = ['is_working', 'start_time', 'end_time']
        widgets = {
            'is_working': forms.CheckboxInput(attrs={'class': 'form-check-input working-toggle'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control time-input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control time-input', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_working = cleaned_data.get('is_working')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if is_working and start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("Start time must be before end time.")
        return cleaned_data


class BlockedDateForm(forms.ModelForm):
    class Meta:
        model = BlockedDate
        fields = ['date', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Personal holiday, Equipment maintenance'}),
        }

    def clean_date(self):
        target_date = self.cleaned_data.get('date')
        if target_date and target_date < date.today():
            raise ValidationError("You cannot block dates in the past.")
        return target_date

