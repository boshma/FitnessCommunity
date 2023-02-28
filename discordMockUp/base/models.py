from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Topic(models.Model):
  name = models.CharField(max_length=200)

  def __str__(self):
    return self.name


class Room(models.Model):
  host =  models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
  topic = models.ForeignKey(Topic, on_delete = models.SET_NULL, null = True)
  name = models.CharField(max_length=200) #max_length required
  description = models.TextField(null = True, blank = True) #null is default False , true means it can be blank
  participants = models.ManyToManyField(User, related_name='participants', blank=True) #related name needed because we already use User above
  updated = models.DateTimeField(auto_now=True) #when save is called, take timestamp
  created = models.DateTimeField(auto_now_add=True) #takes timestamp when created

  class Meta:
    ordering = ['-updated', '-created'] #dash creates it in descending order

  def __str__(self):
    return self.name

class Message(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  room = models.ForeignKey(Room, on_delete = models.CASCADE ) #when room gets deleted, all children get deleted
  body = models.TextField()
  updated = models.DateTimeField(auto_now=True) #when save is called, take timestamp
  created = models.DateTimeField(auto_now_add=True) #takes timestamp when created
  class Meta:
    ordering = ['-updated', '-created'] #dash creates it in descending order

  def __str__(self):
    return self.body[0:50]