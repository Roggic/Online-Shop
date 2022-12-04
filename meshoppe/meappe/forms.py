from datetime import datetime
from django import forms

from .models import *


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'in_stock', 'console', 'genre',
                  'localization', 'release_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'price': forms.NumberInput,
            'release_date': forms.SelectDateWidget(years=[i for i in range(datetime.now().year + 5, 1969, -1)]),
            'description': forms.Textarea(attrs={'cols': 95, 'rows': 14}),
        }


class ImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    class Meta:
        model = Image
        fields = ('image',)
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True, 'accept': 'image/jpeg, image/png, image/webp'}),
        }
