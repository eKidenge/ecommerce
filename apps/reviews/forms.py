from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'pros', 'cons']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)]),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your review here...'
            }),
            'pros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What did you like?'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What could be improved?'
            }),
        }