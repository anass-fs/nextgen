from django import forms
from django.utils import timezone
from datetime import timedelta
from apps.posts.models import Post, Story

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("post_type", "title", "description", "image")
        labels = {
            "post_type": "Type",
            "title": "Titre",
            "description": "Description",
            "image": "Image",
        }
        widgets = {
            "post_type": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Titre de votre publication",
                    "class": "form-control",
                    "maxlength": 255,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Description (minimum 10 caracteres)",
                    "class": "form-control",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }

    def clean_title(self):
        v = self.cleaned_data["title"].strip()
        if len(v) < 3:
            raise forms.ValidationError("Le titre doit contenir au moins 3 caracteres.")
        return v

    def clean_description(self):
        v = self.cleaned_data["description"].strip()
        if len(v) < 10:
            raise forms.ValidationError("La description doit contenir au moins 10 caracteres.")
        return v


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ("content", "image")
        widgets = {
            "content": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 240,
                    "placeholder": "Share a quick update for the next 24 hours...",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("content") and not cleaned.get("image"):
            raise forms.ValidationError("Add text or an image to publish a story.")
        return cleaned

    def save(self, commit=True):
        self.instance.expires_at = timezone.now() + timedelta(hours=24)
        return super().save(commit=commit)
