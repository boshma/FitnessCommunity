from pydoc import describe
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib .auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm



# rooms = [
#     {'id' : 1, 'name':'Lets train chest'},
#     {'id' : 2, 'name':'train with me'},
#     {'id' : 3, 'name':'Cutting advice'},

# ]


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False) #freezes time to get user object and clean data
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form' : form})

def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':
        username = email = request.POST.get('username')
        password = email = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')

    context ={'page' : page}
    return render (request, 'base/login_register.html', context)


# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else  ''
    rooms = Room.objects.filter(
    Q(topic__name__icontains = q) | #or statement
    Q(name__icontains=q) | 
    Q(description__icontains=q)) #model manager/ i = case insensitve
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.all() #activity feed
    context = {'rooms': rooms , 'topics' : topics, 'room_count' : room_count,
     'room_messages' : room_messages}
    return render(request, 'base/home.html', context) #specify what we we're passing in and what it'll be named in the template

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() #message = lower case for some reason
    
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')

        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id) #redirect needed for proper processing



    context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login') #redirects to login page if logged out
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('home')
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance = room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid:
            form.save()
            return redirect('home')

    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : room}) #dynamic obj

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here')

    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : message})