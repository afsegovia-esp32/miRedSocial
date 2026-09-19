from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

class MyConversationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        conversations = (
            Conversation.objects.filter(user1=user) | Conversation.objects.filter(user2=user)
        ).order_by('-created_at')
        return Response(
            ConversationSerializer(conversations, many=True, context={"request": request}).data,
            status=200
        )

class StartConversationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        me = request.user

        if me.id == user_id:
            return Response({"error": "No puedes conversar contigo mismo"}, status=400)

        try:
            other = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario inexistente"}, status=404)

        convo = (
            Conversation.objects.filter(user1=me, user2=other).first()
            or Conversation.objects.filter(user1=other, user2=me).first()
        )

        if convo:
            return Response(ConversationSerializer(convo, context={'request': request}).data, status=200)

        convo = Conversation.objects.create(user1=me, user2=other)
        return Response(ConversationSerializer(convo, context={'request': request}).data, status=201)

class ConversationsMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, convo_id):
        try:
            convo = Conversation.objects.get(id=convo_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversacion inexistente"}, status=404)

        if request.user not in [convo.user1, convo.user2]:
            return Response({"error": "No tiene permiso"}, status=403)

        messages = convo.messages.all().order_by("created_at")
        return Response(MessageSerializer(messages, many=True).data, status=200)


class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, convo_id):
        try:
            convo = Conversation.objects.get(id=convo_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversacion inexistente"}, status=404)

        if request.user not in [convo.user1, convo.user2]:
            return Response({"error": "No tiene permiso"}, status=403)

        serializer = CreateMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        message = Message.objects.create(
            conversation=convo,
            sender=request.user,
            content=serializer.validated_data["content"]
        )
        return Response(MessageSerializer(message).data, status=201)
