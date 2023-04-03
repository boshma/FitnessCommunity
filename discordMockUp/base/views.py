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



def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm() #built in form
    if request.method == "POST": #if form is submitted
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False) #freezes time to get user object and clean data
            user.username = user.username.lower() #lowercase username
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
        
        # Check if user exists and password matches
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username and/or password')

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
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) #activity feed
    context = {'rooms': rooms , 'topics' : topics, 'room_count' : room_count,
     'room_messages' : room_messages}
    return render(request, 'base/home.html', context) #specify what we we're passing in and what it'll be named in the template

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() #message = lower case for some reason
    
    participants = room.participants.all() #for many to many, set not needed
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')

        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id) #redirect needed for proper processing



    context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants} #passing in room object
    return render(request, 'base/room.html', context) #passing in room object   

def userProfile(request, pk): #pk = primary key
    user = User.objects.get(id=pk) #gets user by id
    rooms = user.room_set.all() # gets all the child rooms of user by using the '(child)_set.all()'
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user, 'rooms' : rooms, 'room_messages' : room_messages, 'topics' : topics}

    return render(request, 'base/profile.html', context)

@login_required(login_url='login') #redirects to login page if logged out
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        form = RoomForm(request.POST) #creates form with data from request
        topics = Topic.objects.all()
        if form.is_valid: #checks if all fields are 
            topic_name = request.POST.get('topic')
            topic, created = Topic.objects.get_or_create(name = topic_name) #gets topic or creates it

            Room.objects.create(
                host = request.user,
                topic = topic,
                name = request.POST.get('name'),
                description = request.POST.get('description'),
            )
          
            return redirect('home')
    context = {'form' : form, 'topics' : topics }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance = room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name) #gets topic or creates it
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')

    context = {'form' : form, 'topics' : topics, 'room' : room}
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