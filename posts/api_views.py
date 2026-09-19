from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *


class CreatePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get("content", '')
        image = request.FILES.get("image")

        if not content and not image:
            return Response({"error": "El post debe tener texto o imagen"}, status=400)

        post = Post.objects.create(author=request.user, content=content, image=image)
        return Response(PostSerializer(post).data, status=201)

class FeedPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all().order_by("-created_at")     # TODOS los posts
        return Response(PostSerializer(posts, many=True).data, status=200)


class MyPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(author=request.user).order_by("-created_at")  # SOLO los míos
        return Response(PostSerializer(posts, many=True).data, status=200)

class CreateCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        content = request.data.get("content", '')
        if not content:
            return Response({"error": "El comentario no puede estar vacio"}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': "Post no encontrado"}, status=404)

        comment = Comment.objects.create(post=post, author=request.user, content=content)
        return Response(CommentSerializer(comment).data, status=201)


class PostCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': "Post no encontrado"}, status=404)

        comments = post.comments.all().order_by("created_at")
        return Response(CommentSerializer(comments, many=True).data)