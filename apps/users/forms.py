from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from apps.users.models import Profile
import re

User = get_user_model()

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "username",
                "placeholder": "you@example.com",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "current-password",
                "placeholder": "••••••••",
            }
        ),
    )

def _skills_from_text(text: str) -> list[str]:
    if not text or not str(text).strip():
        return []
    parts = [s.strip() for s in re.split(r"[,;\n]+", str(text)) if s.strip()]
    out = []
    for item in parts[:100]:
        if len(item) > 100:
            raise forms.ValidationError("Each skill must be 100 characters or fewer.")
        out.append(item)
    return out

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "new-password", "placeholder": "Minimum 8 characters"}
        ),
    )
    password_confirm = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "username", "placeholder": "Pseudo"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "autocomplete": "email", "placeholder": "you@example.com"}
            ),
        }

    def clean(self):
        data = super().clean()
        if not data:
            return data
        p1 = data.get("password")
        p2 = data.get("password_confirm")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError({"password_confirm": "Passwords do not match."})
        if p1:
            validate_password(p1)
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
        }

class ProfileEditForm(forms.ModelForm):
    skills_text = forms.CharField(
        label="Compétences",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "python, django, react… (séparées par des virgules)",
            }
        ),
    )

    class Meta:
        model = Profile
        fields = ("bio", "avatar")
        widgets = {
            "bio": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Quelques mots sur vous…"}
            ),
            "avatar": forms.FileInput(attrs={"class": "form-control form-control-file"}),
        }

    def clean_avatar(self):
        """Valide la taille de l'avatar (max 5MB)."""
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > 5 * 1024 * 1024:  # 5 MB
                raise forms.ValidationError("L'image ne doit pas dépasser 5 Mo.")
            # Vérifier l'extension
            import os
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise forms.ValidationError("Format d'image non supporté (jpg, jpeg, png, gif, webp uniquement).")
        return avatar

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.skills:
            self.fields["skills_text"].initial = ", ".join(self.instance.skills)

    def clean(self):
        super().clean()
        text = self.cleaned_data.get("skills_text", "")
        try:
            self.cleaned_data["skills_parsed"] = _skills_from_text(text)
        except forms.ValidationError as e:
            self.add_error("skills_text", e)
        return self.cleaned_data

    def save(self, commit=True):
        if "skills_parsed" in self.cleaned_data:
            self.instance.skills = self.cleaned_data["skills_parsed"]
        return super().save(commit=commit)
