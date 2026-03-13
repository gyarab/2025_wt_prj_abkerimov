from django import forms
from .models import Playlist
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control bg-dark text-light border-secondary'})
            
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'is_public'] # Uživatel zadává jen název a jestli je veřejný
        labels = {
            'name': 'Název playlistu',
            'is_public': 'Veřejný playlist (uvidí ho i ostatní)',
        }
        # Přidáme Bootstrap CSS třídy, aby to vypadalo dobře v našem tmavém vzhledu
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input bg-dark border-secondary'}),
        }