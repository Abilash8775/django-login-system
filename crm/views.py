from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from login import settings 
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from .tokens import generate_token
# Create your views here.
def home(request):
    return render(request, "crm/index.html")
def signup(request):
    if request.method=="POST":
        username=request.POST['username']
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        email=request.POST['email']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists")
            return redirect('home')
            
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered")
            return redirect('home')
        if len(username)>10:
            messages.error(request, 'Username uns=der 10 char')
            
        if pass1 != pass2:
            messages.error(request, "passwords didn't match !")
        
        myuser=User.objects.create_user(username,email,pass1)
        myuser.first_name=firstname
        myuser.is_active=False
        myuser.last_name=lastname
        
        myuser.save()
        
        messages.success(request, "Your account has been created. Email have been sent")
        
        subject="welcome to CRM- django template"
        message = "Hello"+ myuser.first_name + "!! \n"+ "welcome to CRM!!  \n Thank you for visiting our website" 
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        current_site=get_current_site(request)
        email_subject="confirm your email"
        message2=render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })
        email = EmailMessage={
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        }
        email.fail_silently = True
        email.send()
        return redirect("/signin")
    
    return render(request, "crm/signup.html")
def signin(request):
    if request.method=="POST":
        username=request.POST['username']
        pass1=request.POST['pass1']
        
        user=authenticate(username=username , password=pass1)
        
        if user is not None:
            login(request,user)
            firstname=User.first_name
            return render(request, "crm/index.html",{"firstname":firstname})
        else:
            messages.error(request, "Invalid credentials")
            return redirect('home')
        
    return render(request, "crm/signin.html")
def signout(request):
    logout(request)
    messages.success(request, "LOGOUT SUCCESSFUL")
    return redirect('home')
def activate(request, uidb64):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        myuser=User.obkects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser=None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active =True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation failed.html')