from django.shortcuts import render,redirect
from .models import todo,PasswordResetOTP, Query, Donation, CustomUser as User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import random
from decouple import config
import stripe
from home.utils.email_utils import send_email_async

stripe.api_key = settings.STRIPE_API_KEY


# Create your views here.
def home(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request,"Please login to add to-do item")
            return redirect('/todo')

        data = request.POST

        title = data.get('title').strip()
        description = data.get('description').strip()
        user = request.user

        if len(description) == 0:
            description = "Default description(Please add description)"

        print(title)
        print(len(description))

        if not title:
            messages.error(request,"Please Enter Title")
            return redirect("/todo")
        
        item = todo.objects.create(
            title = title,
            description = description,
            status = "In Progress",
            user = user
        )

        print(item)
        messages.success(request,"Item successfully added.")

        return redirect("/todo")

    return render(request,"home.html")


@login_required(login_url="/login")
def delete_item(request,id):
    print(id)
    item = todo.objects.get(id = id)
    item.delete()

    return redirect('/todo/all_todos')


@login_required(login_url="/login")
def update_status_to_finish(request,id):
    print(id)
    item = todo.objects.get(id = id)
    item.status = "Finished"
    item.save()

    return redirect('/todo/all_todos')


@login_required(login_url="/login")
def update_status_to_progress(request,id):
    print(id)
    item = todo.objects.get(id = id)
    item.status = "In Progress"
    item.save()

    return redirect('/todo/all_todos')


def login_page(request):
    if request.method == "POST":
        # Getting data from the request
        user_data = request.POST

        # Assigning data to each variable
        username = user_data.get('username')
        password = user_data.get('password')

        user = authenticate(username = username,password = password)

        if not user:
            messages.error(request,"Invalid username or password")
            return redirect("/login")
        
        else:
            login(request,user)
            return redirect("/todo")
        
    return render(request,"login.html")


def logout_page(request):
    logout(request)
    return redirect("/login")


def register(request):
    if request.method == "POST":
        # Getting data from the request
        user_data = request.POST

        # Assigning data to each variable
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        username = user_data.get('username')
        password = user_data.get('password')
        email = user_data.get('email')

        # Checking if username exists
        user = User.objects.filter(username = username)

        if user.exists():
            messages.info(  request,"Username already exists")
            return redirect("/register")

        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
        )

        user.set_password(password)

        user.save()

        send_email_async(
            subject='Thanks for joining TO-DO community',
            message=f'Hi {first_name},\nYou have successfully registered with us. Welcome to the community.\nThanks for choosing us',
            from_email= config("MY_EMAIL"),
            recipient_list=[email],
        )

        messages.info(request,"Account Created successfully.Please login")

        return redirect("/login")


    return render(request,"register.html")


def show_all_todos(request):
    if not request.user.is_authenticated:
        messages.info(request,"Please login to see to-do item")
        return redirect('/todo')
    
    sort_by = request.GET.get('sort_by', 'date_created')
    if sort_by not in ['date_created', '-date_created','status','-status']:
        sort_by = 'date_created'
    
    allTODO = todo.objects.filter(user = request.user).order_by(sort_by)
    context = {
        "items" : allTODO,
        'sort_by': sort_by
    }
    return render(request,"all_todos.html",context)


@login_required(login_url="/login")
def profile(request):
    user = request.user
    queries = Query.objects.filter(user = user)
    donations = Donation.objects.filter(user = user)

    context = {
        "user" : user,
        "queries" : queries,
        "donations" : donations,
    }
    return render(request,"profile.html",context)


@login_required(login_url="/login")
def update_todo(request,id):
    item = todo.objects.get(id= id)
    context = {
        "item" : item
    }

    if request.method == "POST":
        data = request.POST
        title = data.get('title')
        description = data.get('description')

        item.description = description
        item.title = title

        item.save()

        messages.info(request,"Update successfully")

        return render(request,"update_todo.html",context)

    return render(request,"update_todo.html",context)


def forget_password(request):
    if request.method == "POST":
        data = request.POST
        username = data.get('username')

        user = User.objects.filter(username = username)

        if not user:
            messages.info(request,"User does not exists")
            return redirect("/forget-password")
        
        else:
            try:
                user = user[0]
                email = user.email
                first_name = user.first_name

                otp = str(random.randint(100000, 999999))
                print("OTP ->",otp)

                PasswordResetOTP.objects.create(user=user, otp=otp)

                send_mail(
                    subject='OTP for Password Reset',
                    message=f'Hi {first_name},\nYour OTP to reset the password on To-Do app : {otp}\nThanks for choosing us',
                    from_email= config("MY_EMAIL"),
                    recipient_list=[email],
                )

                return redirect(f"/forget-password/{username}")
            
            except Exception as e:
                print(e)
                messages.info(request,"Some error occured! Please try again")
                return render(request,"forget_password.html")       

    return render(request,"forget_password.html")


def forget_password_authenticate(request,username):
    if request.method == "POST":
        data = request.POST
        otp = data.get('otp')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            messages.error(request,"Password and confirm password does not match")
            return render(request,"forget_password_authenticate.html")
        
        user = User.objects.filter(username = username)
        user = user[0]

        if not PasswordResetOTP.objects.filter(user = user).exists():
            messages.info(request,"Did not able to get the OTP. Kindly start from the beginning.")
            return redirect("/forget-password")
        
        original_otp = PasswordResetOTP.objects.filter(user = user)

        original_otp = original_otp[0]

        otp_from_db = int(original_otp.otp)
        otp = int(otp)

        if otp_from_db != otp:
            messages.info(request,"Wrong OTP. Please try again")
            return render(request,"forget_password_authenticate.html")

        user.set_password(password)
        user.save()

        original_otp.delete()

        messages.info(request,"Password reset done. Please login")
        return redirect("/login")

    return render(request,"forget_password_authenticate.html")


def policy(request):
    return render(request,"policy.html")


@login_required(login_url="/login")
def delete_account(request,username):
    user = request.user
    user.delete()

    send_email_async(
        subject='Thanks for joining TO-DO community',
        message=f'Hi {user.first_name},\nIt is hard to let you go. Your account and data related to it is successfully deleted.\nPlease sign up again if you need us.\n Thanks for connecting with us.',
        from_email= config("MY_EMAIL"),
        recipient_list=[user.email],
    )

    messages.info(request,"Successfully deleted account")
    return redirect("/todo")


@login_required(login_url="/login")
def update_account(request,username):
    if request.method == "POST":
        data = request.POST
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        user_description = data.get('user_description')
        user = request.user

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.user_description = user_description

        user.save()

        messages.info(request,"Profile updated successfully.")
        return redirect("/profile")

    return render(request,"update_account.html")


def about(request):
    return render(request,"about.html")


@login_required(login_url="/login")
def contact_us(request):
    if request.method == "POST":
        try:
            data = request.POST

            user = request.user
            title = data.get('title')
            description = data.get('message')

            query = Query.objects.create(
                user = user,
                title = title,
                description = description
            )

            send_email_async(
                subject='Thanks for contacting TO-DO team',
                message=f'Hi {user.first_name},\nHope you are doing well. We have recieved your message.\nTitle: {title}\nMessage: {description}\nThanks for choosing us. Have a nice day.',
                from_email= config("MY_EMAIL"),
                recipient_list=[user.email],
            )

            messages.info(request,"Message sent successfully")
            return redirect("/profile")

        except Exception as e:
            print(e)
            messages.info(request,"Something wrong happened. Please try again")
            return redirect("/todo/contact-us")

    return render(request,"contact_us.html")


@login_required(login_url="/login")
def payment(request):
    if request.method == "POST":
        try:
            data = request.POST
            amount = data.get('amount')
            email = request.user.email

            if not amount:
                messages.info(request,"Please enter amount .")
                return redirect("/todo/donate")
            
            amount = int(amount)

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': amount*100,
                            'product_data': {
                                'name': 'Donation'
                            },
                        },
                        'quantity': 1,
                    },
                ],
                customer_email = email,
                mode='payment',
                success_url='http://localhost:8000/todo/donate/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:8000/todo/donate/failed',
            )
        except Exception as e:
            print(e)
            messages.info(request,"Error occurred. Please try again.")
            return redirect("/todo/donate")

        return redirect(checkout_session.url)
    return render(request,"donate.html")


@login_required(login_url="/login")
def payment_success(request):
    session_id = request.GET.get('session_id')
    user = request.user
    session = stripe.checkout.Session.retrieve(session_id)
    email = session.get("customer_email")
    amount = session.get("amount_total")

    Donation.objects.create(
        amount = amount,
        user =  user
    )

    messages.info(request,"Payment successfully done. Thanks for your contribution.")
    return redirect("/todo")


@login_required(login_url="/login")
def payment_failed(request):
    messages.info(request,"Payment Error. Please try again.")
    return redirect("/todo/donate")


@login_required(login_url="/login")
def change_password(request):
    if request.method == "POST":
        data = request.POST
        password = data.get('password')
        new_password = data.get('new_password').strip()
        confirm_password = data.get('confirm_password').strip()
        user = request.user

        isCorrectPassword = user.check_password(password)
        if not isCorrectPassword:
            messages.info(request,"Incorrect password")
            return redirect("/change-password")
        
        if not new_password:
            messages.info(request,"Please add new password")
            return redirect("/change-password")
        
        if new_password != confirm_password :
            messages.info(request,"New password and Confirm Password does not match!")
            return redirect("/change-password")
        
        user.set_password(new_password)
        user.save()

        send_email_async(
            subject='Password reset on To-Do app',
            message=f'Hi {user.first_name},\nYou have successfully changed your password.\nThanks for choosing us',
            from_email= config("MY_EMAIL"),
            recipient_list=[user.email],
        )

        login(request,user)

        messages.info(request,"Password successfully changed. Please login again.")
        return redirect("/profile")


    return render(request,"change_password.html")
