from django import forms
from apps.interactions.models import Comment, DirectMessage

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 2,
                    "maxlength": 4000,
                    "placeholder": "Write a thoughtful and helpful comment...",
                }
            )
        }

    def clean_body(self):
        value = self.cleaned_data["body"].strip()
        if len(value) < 1:
            raise forms.ValidationError("The comment cannot be empty.")
        return value


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 3,
                    "maxlength": 4000,
                    "placeholder": "Write your message...",
                }
            )
        }

    def clean_body(self):
        value = self.cleaned_data["body"].strip()
        if len(value) < 1:
            raise forms.ValidationError("The message cannot be empty.")
        return value
