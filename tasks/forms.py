from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="El. paštas",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Toks el. paštas jau naudojamas.")

        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "content", "priority", "due_date", "is_done"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_done": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }