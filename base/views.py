from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, JoinRequest
from .forms import RoomForm, UserForm, MyUserCreationForm

FALLBACK_ACTIVITIES = [
    {
        'type': 'sample',
        'username': 'alex',
        'time': 'just now',
        'title': 'Welcome to StudyBud',
        'body': 'Create a room to see live activity here.',
    },
    {
        'type': 'sample',
        'username': 'morgan',
        'time': '10 minutes ago',
        'title': 'Django study group',
        'body': 'Recent replies and new rooms will appear in this feed.',
    },
    {
        'type': 'sample',
        'username': 'sam',
        'time': '1 hour ago',
        'title': 'Python basics',
        'body': 'This sample disappears as real activity is added.',
    },
]


def get_recent_activities(q='', limit=3):
    room_filter = (
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    message_filter = Q(room__topic__name__icontains=q)

    rooms = Room.objects.filter(room_filter).select_related('host', 'topic')[:limit]
    messages = (
        Message.objects
        .filter(message_filter)
        .select_related('user', 'room')
        [:limit]
    )

    activities = [
        {'type': 'room', 'created': room.created, 'room': room, 'user': room.host}
        for room in rooms
    ]
    activities.extend(
        {
            'type': 'message',
            'created': message.created,
            'message': message,
            'room': message.room,
            'user': message.user,
        }
        for message in messages
    )

    activities.sort(key=lambda activity: activity['created'], reverse=True)
    return activities[:limit]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Please fix the registration errors below.')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = list(Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ))

    join_request_map = {}
    if request.user.is_authenticated:
        join_request_map = {
            join_request.room_id: join_request.status
            for join_request in JoinRequest.objects.filter(
                user=request.user,
                room__in=rooms,
            )
        }
        for room in rooms:
            room.join_request_status = join_request_map.get(room.id)
            room.is_joined_by_request_user = room.participants.filter(
                id=request.user.id,
            ).exists()
    else:
        for room in rooms:
            room.join_request_status = None
            room.is_joined_by_request_user = False

    topics = Topic.objects.all()[0:5]
    room_count = len(rooms)
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]
    recent_activities = get_recent_activities(q)

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages,
               'recent_activities': recent_activities,
               'fallback_activities': FALLBACK_ACTIVITIES,
               'show_join_controls': True}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    recent_activities = get_recent_activities(limit=3)
    topics = Topic.objects.all()
    pending_invites = JoinRequest.objects.filter(
        room__host=user,
        status=JoinRequest.PENDING,
    ).select_related('room', 'user')
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics,
               'recent_activities': recent_activities,
               'fallback_activities': FALLBACK_ACTIVITIES,
               'pending_invites': pending_invites}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def requestJoinRoom(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.method != 'POST':
        return redirect('home')

    if room.host == request.user:
        messages.info(request, 'You already own this room.')
        return redirect('home')

    if room.participants.filter(id=request.user.id).exists():
        messages.info(request, 'You already joined this room.')
        return redirect('home')

    join_request, created = JoinRequest.objects.get_or_create(
        room=room,
        user=request.user,
        defaults={'status': JoinRequest.PENDING},
    )

    if not created and join_request.status != JoinRequest.PENDING:
        join_request.status = JoinRequest.PENDING
        join_request.save(update_fields=['status', 'updated'])

    messages.success(request, f'Join request sent to {room.host.username}.')
    return redirect('home')


@login_required(login_url='login')
def updateJoinRequest(request, pk, action):
    join_request = get_object_or_404(
        JoinRequest.objects.select_related('room', 'user'),
        id=pk,
    )

    if request.method != 'POST':
        return redirect('user-profile', pk=request.user.id)

    if join_request.room.host != request.user:
        return HttpResponse('Your are not allowed here!!')

    if action == 'accept':
        join_request.status = JoinRequest.ACCEPTED
        join_request.room.participants.add(join_request.user)
        messages.success(
            request,
            f'Accepted @{join_request.user.username} into {join_request.room.name}.',
        )
    elif action == 'reject':
        join_request.status = JoinRequest.REJECTED
        messages.info(
            request,
            f'Rejected @{join_request.user.username} request for {join_request.room.name}.',
        )
    else:
        return HttpResponse('Invalid invite action.')

    join_request.save(update_fields=['status', 'updated'])
    return redirect('user-profile', pk=request.user.id)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    recent_activities = get_recent_activities(limit=3)
    return render(request, 'base/activity.html', {
        'recent_activities': recent_activities,
        'fallback_activities': FALLBACK_ACTIVITIES,
    })
