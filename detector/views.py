from django.shortcuts import render, redirect
from .models import UserDetails
from django.core.mail import send_mail
from django.conf import settings
import os
import random
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from tensorflow import keras
import cv2

BASE_DIR = Path(__file__).resolve().parent.parent

def index(request):
    return render(request, 'frontpage.html')

def SignedUpEmail(request):
    status = 0
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password1']
        user_name = first_name.capitalize() + " "+ last_name.capitalize()
        if UserDetails.objects.filter(user_email=email):
            status = 1
            return render(request,"signedbyemail.html",{"status":status})
        else:
            status = 2
            if len(password)<8:
                return render(request,"signedbyemail.html",{"status":status})
            else:
                user = UserDetails(user_name=user_name,user_email=email,user_password=password)
                user.save()
                return redirect("/loginpage")
    else:
        return render(request,"signedbyemail.html",{"status":status})

def Logedin(request):
    status = False
    if request.method == 'POST':
        email = request.POST['login']
        password = request.POST['password']
        user_data = UserDetails.objects.filter(user_email=email,user_password=password)
        if user_data:
            request.session['user_name'] = email
            request.session['user_pass'] = password
            return redirect('/mainpage')
        else:
            status = True
            return render(request,'logedin.html',{'status':status})
    return render(request,'logedin.html',{'status':status})

def Forgotpass(request):
    status = False
    if request.method == "POST":
        otp = random.randint(0,10000)
        email = request.POST["email"]
        emails = f"{email}{str(otp)}"
        find_email = UserDetails.objects.filter(user_email=email)
        if find_email:
            subject = "This mail regarding the change of your django app password"
            message = f"The otp for changing your django app password {otp}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject,message,from_email,recipient_list)
            return redirect(f'/resetpass/{emails}')
        else:
            status = True
            return render(request,"forgotpass.html",{"status":status})
    return render(request,"forgotpass.html",{"status":status})

def Resetpass(request,emails):
    status = False
    emails = emails
    otp = ""
    index = 0
    for i in range(len(emails)-1,-1,-1):
        if emails[i].isdigit():
            otp += emails[i]
        else:
            index = i
            break
    otp = otp[::-1]
    email = emails[:index+1]
    if request.method == "POST":
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        otp1 = request.POST["otp"]
        if password1==password2 and int(otp1) == int(otp):
            user_id = list(UserDetails.objects.filter(user_email = email).values())[0]["id"]
            user_name = list(UserDetails.objects.filter(user_email = email).values())[0]["user_name"]
            user = UserDetails(id = user_id,user_name = user_name,user_email= email,user_password=password1)
            user.save()
            return redirect('/loginpage')
        else:
            status = True
            return render(request,"resetpass.html",{"email":email,"status":status})
    else:
        return render(request,"resetpass.html",{"email":email,"status":status})
    
def Mainpage(request):
    email = request.session.get('user_name')[0].capitalize()
    email_id = request.session.get('user_name')
    status = False
    if request.method == 'POST':
        if request.POST['logout'] == 'logout':
            path = f"{BASE_DIR}/media"
            for filename in os.listdir(path):
                if os.path.isfile(os.path.join(path, filename)):
                    os.remove(os.path.join(path, filename))
            del request.session['user_name']
            del request.session['user_pass']
            return redirect('/')
        else:
            if request.FILES['image_uploaded']:
                try:
                    status = True
                    image = request.FILES['image_uploaded']
                    fs = FileSystemStorage()
                    image_name = "_".join(image.name.split(" "))
                    filename = fs.save(image_name, image)
                    image_path = f'{BASE_DIR}{fs.url(filename)}'.replace("\\",'/')
                    model = keras.layers.TFSMLayer("EfficientNetModel", call_endpoint='serving_default')
                    image = cv2.imread(image_path)
                    target_size = (32, 32)
                    resized_image = cv2.resize(image, target_size)
                    test_image = resized_image.reshape((1, *target_size, 3))
                    predictions = model(test_image)
                    tensor = predictions['dense_3']
                    predictions_array = tensor.numpy()
                    real_percentage = round(predictions_array[0][1]*100)
                    fake_percentage = round(predictions_array[0][0]*100)
                    # os.remove(image_path)
                    return render(request,'mainpage.html',{'email':email, "status":status,"real":real_percentage,"fake":fake_percentage,"image_path":fs.url(filename)})
                except:
                    status = False
                    os.remove(image_path)
                    return render(request,'mainpage.html',{'email':email,"status":status}) 
            else:
                return render(request,'mainpage.html',{'email':email,"status":status})  
    else:
        return render(request,'mainpage.html',{'email':email, "status":status})