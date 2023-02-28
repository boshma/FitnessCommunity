from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
  class Meta:
    model = Room
    fields = '__all__' #creates all fields from Room (host, topic, name etc)
    exclude = ['host', 'participants']
