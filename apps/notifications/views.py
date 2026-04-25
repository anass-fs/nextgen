from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

class NotificationListView(LoginRequiredMixin, TemplateView):
    template_name = "web/notifications.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        notifications = self.request.user.notifications.select_related("actor", "post")
        ctx["notifications"] = notifications
        return ctx


class MarkNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request):
        request.user.notifications.filter(read=False).update(read=True)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "ok"})
        return redirect("notifications")
