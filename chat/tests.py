from django.test import TestCase
from rest_framework.test import APITestCase

from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User

from .models import *
from .serializers import *

# Create your tests here.


class NoAutoChatTests(APITestCase):

    def setUp(self):
        self.usr1 = User.objects.create_user(username='usr1', password='clave12345')
        self.client.force_authenticate(user=self.usr1)
    
    def test_no_iniciar_chat_con_uno_mismo(self):
        url = reverse('chat_api:start_conversation', args=[self.usr1.id])
        respuesta = self.client.post(url)

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Conversation.objects.count(), 0)


class AislamientoConversaciones(APITestCase):
    def setUp(self):
        self.usr2 = User.objects.create_user(username='usr2', password='clave12345')
        self.usr3 = User.objects.create_user(username='usr3', password='clave12345')
        self.usr4 = User.objects.create_user(username='usr4', password='clave12345')

        self.conversacion = Conversation.objects.create(user1=self.usr3, user2=self.usr4)
        Message.objects.create(
            conversation=self.conversacion,
            sender=self.usr3,
            content='Hola usr4, este mensaje es privado'
        )
        
        self.client.force_authenticate(user=self.usr2)
        

    def test_no_puede_ver_mensajes_ajenos(self):
        url = reverse('chat_api:conversations_messages', args=[self.conversacion.id])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_puede_enviar_mensajes_ajenos(self):
        url = reverse('chat_api:send_message', args=[self.conversacion.id])
        respuesta = self.client.post(url, {"content":"Mensaje de un intruso"})
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Message.objects.filter(content='Mensaje de un intruso').count(), 1
        )

