from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from home.models import todo, Query, Donation, CustomUser as User
from home.utils.email_utils import send_email_async
from django.contrib import messages
from django.db.models import Q


def is_admin(user):
    return user.is_authenticated and user.isAdmin

@user_passes_test(is_admin)
@login_required(login_url="/login")
def admin_portal(request):
    username = request.GET.get('q')
    
    user = request.user

    if username:
        allTodos = todo.objects.filter(Q(user__username__icontains = username))
        allUsers = User.objects.filter(Q(username__icontains  = username))
        allQuery = Query.objects.filter(Q(user__username__icontains  = username))
        allDonations = Donation.objects.filter(Q(user__username__icontains  = username))
    else:
        allTodos = todo.objects.all()[:10]
        allUsers = User.objects.all()[:10]
        allQuery = Query.objects.all()[:10]
        allDonations = Donation.objects.all()[:10]

    context = {
        "user" : user,
        "allTodos" : allTodos,
        "allUsers" : allUsers,
        "allQuery" : allQuery,
        "allDonations" : allDonations,
        "username" : username
    }

    return render(request,"admin_portal.html",context)


@user_passes_test(is_admin)
@login_required(login_url="/login")
def all_users(request):
    user = request.user
    allUsers = User.objects.all()

    context = {
        "user" : user,
        "allUsers" : allUsers,
    }

    return render(request,"all_users.html",context)


@user_passes_test(is_admin)
@login_required(login_url="/login")
def all_query(request):
    user = request.user
    allQuery = Query.objects.all()

    context = {
        "user" : user,
        "allQuery" : allQuery,
    }

    return render(request,"all_query.html",context)


@user_passes_test(is_admin)
@login_required(login_url="/login")
def all_donations(request):
    user = request.user
    allDonations = Donation.objects.all()

    context = {
        "user" : user,
        "allDonations" : allDonations,
    }

    return render(request,"all_donations.html",context)


@user_passes_test(is_admin)
@login_required(login_url="/login")
def all_todos(request):
    sort_by = request.GET.get('sort_by', 'date_created')
    if sort_by not in ['date_created', '-date_created','status','-status']:
        sort_by = 'date_created'
    
    user = request.user
    allTodos = todo.objects.all().order_by(sort_by)

    context = {
        "user" : user,
        "allTodos" : allTodos,
        'sort_by': sort_by
    }

    return render(request,"all_todos_items.html",context)


@user_passes_test(is_admin)
@login_required(login_url="/login")
def admin_delete_account(request,id):
    user = User.objects.get(id=id)
    # user.delete()

    send_email_async(
        subject='Thanks for joining TO-DO community',
        message=f'Hi {user.first_name},\nYour account is deleted by our Admin.\nPlease sign up again if you need us.\nThanks for connecting with us.',
        from_email= "",
        recipient_list=[user.email],
    )
    next_url = request.GET.get('next', '/admin-portal/all-users')

    return redirect(next_url)


@user_passes_test(is_admin)
@login_required(login_url="/login")
def update_query(request,id):
    query = Query.objects.get(id =id)
    context = {
        "query" : query,
    }

    if request.method == "POST":
        data = request.POST
        status = data.get('status')
        remarks = data.get('remarks')

        query.status = status
        query.remarks = remarks

        query.save()

        send_email_async(
            subject=f'Your query with title "{query.title} is now {query.status}"',
            message=f'Hi {query.user.first_name},\nYour query with title {query.title} is updated.\nThanks for connecting with us.',
            from_email= "",
            recipient_list=[query.user.email],
        )

        messages.info(request,"Query Successfully updated.")
        return redirect(f"/admin-portal/update-query/{query.id}")

    return render(request,"update_query.html",context)

