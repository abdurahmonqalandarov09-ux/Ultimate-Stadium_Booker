from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Count
from .models import *




def home_page(request):
    return render(request, 'home.html')



def register(request):
    if request.method == "POST":
        data = request.POST
        if data:
            if CustomUser.objects.filter(username=data['username']).exists():
                 messages.error(request, "Логин занят")
            CustomUser.objects.create_user(
                username = data['username'],
                password = data['password'],
                email = data['email'],
                photo = request.FILES.get('photo'),
                phone = data['phone'],
                about = data['about']
            )
        
            return redirect('login')
    return render(request, 'registration.html')




def login_user(request):
    if request.method == 'POST':
        data = request.POST
        user = authenticate(request, username = data['username'], password = data['password'])
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Неверный логин или пароль")
    return render(request, 'login.html')



@login_required
def logout_user(request):
    logout(request)
    return redirect('login')




@login_required
def profile(request):
    return render(request, 'profile.html', {
        'bookings_count': request.user.bookings.count(),
    })


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.about = request.POST.get('about', user.about)
        if request.FILES.get('photo'):
            user.photo = request.FILES['photo']
        user.save()
        messages.success(request, "Профиль обновлён")
        return redirect('profile')
    return render(request, 'edit_profile.html', {'user': user})



@login_required
def user_profile(request, pk):
    profile_user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'user_profile.html', {'profile_user': profile_user})






@login_required
def field_list(request):
    if request.method == "GET":
        field = Field.address.all()
        return render(request, 'field_list.html', {'field': field})



@login_required
def field_list(request):
    fields = Field.objects.select_related('category')

    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    sort = request.GET.get('sort', '')
    max_price = request.GET.get('max_price', '')
    min_price = request.GET.get('min_price', '')

    if q:
        fields = fields.filter(Q(name__icontains=q) | Q(address__icontains=q))
    if category:
        fields = fields.filter(category_id=category)
    if status == 'free':
        fields = fields.filter(is_free=True)
    elif status == 'busy':
        fields = fields.filter(is_free=False)
    if sort == 'price_asc':
        fields = fields.order_by('price')
    elif sort == 'price_desc':
        fields = fields.order_by('-price')
    if max_price:
        fields = fields.filter(price__lte=max_price)
    if min_price:
        fields = fields.filter(price__gte=min_price)

    return render(request, "field_list.html", {
        "fields": fields,
        "categories": Category.objects.all(),
        "q": q,
        "category": category,
        "status": status,
        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
    })




@login_required
def field_detail(request, pk):
    field = get_object_or_404(Field.objects.select_related('category'), pk=pk)
    return render(request, 'field_detail.html', {'field': field})




@login_required
def book_field(request, pk):
    field = get_object_or_404(Field, pk=pk)

    if not field.is_free:
        messages.error(request, "Это поле уже занято")
        return redirect('fields')

    if request.method == 'POST':
        has_team = request.POST.get('has_team') == 'yes'
        players_needed = None

        if not has_team:
            value = request.POST.get('players_needed', '')
            if not value.isdigit() or int(value) < 1:
                messages.error(request, "Укажите, сколько игроков не хватает")
                return render(request, 'book_field.html', {'field': field})
            players_needed = int(value)

        Booking.objects.create(
            user=request.user,
            field=field,
            has_team=has_team,
            players_needed=players_needed,
        )
        field.is_free = False
        field.save()
        messages.success(request, "Поле заказано")
        return redirect('my_fields')

    return render(request, 'book_field.html', {'field': field})




@login_required
def my_fields(request):
    bookings = Booking.objects.filter(user=request.user).select_related('field').order_by('-created_at')
    active = bookings.filter(status='active')
    history = bookings.exclude(status='active')
    return render(request, 'my_fields.html', {'active': active, 'history': history})




@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('field', 'user').prefetch_related('participants__user'),
        pk=pk, user=request.user,
    )
    return render(request, 'booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user, status='active')
    booking.status = 'cancelled'
    booking.save()
    booking.field.is_free = True
    booking.field.save()
    messages.success(request, "Заказ отменён")
    return redirect('my_fields')


@login_required
def finish_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user, status='active')
    booking.status = 'completed'
    booking.save()
    booking.field.is_free = True
    booking.field.save()
    messages.success(request, "Игра завершена, поле свободно")
    return redirect('my_fields')




@login_required
def play_together(request):
    bookings = (
        Booking.objects
        .filter(status='active', has_team=False)
        .select_related('field', 'field__category', 'user')
        .prefetch_related('participants__user')
        .annotate(joined=Count('participants'))
        .order_by('-created_at')
    )
    joined_ids = list(
        Participant.objects.filter(user=request.user).values_list('booking_id', flat=True)
    )
    return render(request, 'play_together.html', {
        'bookings': bookings,
        'joined_ids': joined_ids,
    })


@login_required
def join_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, status='active', has_team=False)

    if booking.user == request.user:
        messages.error(request, "Нельзя вступить в свой заказ")
    elif Participant.objects.filter(booking=booking, user=request.user).exists():
        messages.error(request, "Вы уже в этой команде")
    elif booking.participants.count() >= booking.players_needed:
        messages.error(request, "Мест больше нет")
    else:
        Participant.objects.create(booking=booking, user=request.user)
        messages.success(request, "Вы вступили в команду")
    return redirect('play_together')


@login_required
def leave_booking(request, pk):
    participant = get_object_or_404(Participant, booking_id=pk, user=request.user)
    participant.delete()
    messages.success(request, "Вы вышли из команды")
    return redirect('play_together')