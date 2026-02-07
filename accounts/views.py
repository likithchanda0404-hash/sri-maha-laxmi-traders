from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomerProfile


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "accounts/login.html")


def signup(request):
    if request.method == "POST":
        from django.contrib.auth.models import User

        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "accounts/signup.html")


def user_logout(request):
    logout(request)
    return redirect("home")


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.phone = request.POST.get("phone", "").strip()
        profile.address = request.POST.get("address", "").strip()
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "accounts/profile.html", {"profile": profile})
