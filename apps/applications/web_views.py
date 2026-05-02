from django import forms as django_forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.accounts.permissions import is_admin_user

from .models import Application

User = get_user_model()


class ProfileForm(django_forms.Form):
    first_name = django_forms.CharField(label=_("First name"), max_length=150, required=False)
    last_name  = django_forms.CharField(label=_("Last name"),  max_length=150, required=False)
    email      = django_forms.EmailField(label=_("Email"), required=True)
    cv         = django_forms.FileField(
        label=_("Upload CV"),
        required=False,
        widget=django_forms.FileInput(attrs={"accept": ".pdf,.doc,.docx"}),
    )


class PasswordForm(django_forms.Form):
    new_password     = django_forms.CharField(
        label=_("New password"),
        required=True,
        widget=django_forms.PasswordInput(render_value=False,
                                          attrs={"placeholder": _("Enter new password")}),
    )
    confirm_password = django_forms.CharField(
        label=_("Confirm new password"),
        required=True,
        widget=django_forms.PasswordInput(render_value=False,
                                          attrs={"placeholder": _("Repeat new password")}),
    )

    def clean(self):
        cleaned = super().clean()
        pw  = cleaned.get("new_password", "")
        cpw = cleaned.get("confirm_password", "")
        if pw and pw != cpw:
            raise django_forms.ValidationError(_("Passwords do not match."))
        return cleaned


@login_required(login_url="/login.html")
def user_account(request):
    if is_admin_user(request.user):
        return redirect("adminpanel-dashboard")
    user = request.user
    my_apps = (
        Application.objects
        .filter(applicant=user)
        .select_related("job", "job__company")
        .order_by("-applied_at")
    )

    profile_form  = ProfileForm(initial={
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "email":      user.email,
    })
    password_form = PasswordForm()
    open_settings = False

    if request.method == "POST":
        action = request.POST.get("_action", "profile")

        if action == "password":
            password_form = PasswordForm(request.POST)
            open_settings = True
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password"])
                user.save()
                messages.success(request, _("Password changed successfully."))
                return redirect("user-account")
        else:
            profile_form = ProfileForm(request.POST, request.FILES)
            if profile_form.is_valid():
                cd    = profile_form.cleaned_data
                email = cd["email"].strip().lower()

                if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                    messages.error(request, _("That email is already in use by another account."))
                else:
                    user.first_name = cd.get("first_name", "").strip()
                    user.last_name  = cd.get("last_name", "").strip()
                    user.email      = email
                    if cd.get("cv"):
                        user.cv = cd["cv"]
                    user.save()
                    messages.success(request, _("Profile updated successfully."))
                    return redirect("user-account")

    return render(request, "dashboard/account.html", {
        "form":          profile_form,
        "password_form": password_form,
        "applications":  my_apps,
        "open_settings": open_settings,
    })


@login_required(login_url="/login.html")
def user_dashboard(request):
    return redirect("user-account")


@login_required(login_url="/login.html")
def user_applications(request):
    return redirect("user-account")
