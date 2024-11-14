from .models import *
from .serializers import *
from blog.permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

# Post APIView
class PostViewSet(APIView):   
# --------------------------------------------------------------- FOR PERMISSION ---------------------------------------------------------------
    permission_classes = [IsOwnerOrReadOnly]
    def get(self, request, pk=None):
        if pk:
            post = get_object_or_404(Post, pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        else:
            posts = Post.objects.all()
# --------------------------------------------------------------- FOR SEARCH QUERY -------------------------------------------------------------
            search_query = request.query_params.get('search', None)
            if search_query:
                posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query) | Q(author__username__icontains=search_query))
# --------------------------------------------------------------- FOR PAGINATION ---------------------------------------------------------------
            paginator = PageNumberPagination()
            paginator.page_size = 3
            result_page = paginator.paginate_queryset(posts, request)
            serializer = PostSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk=None):
        if request.user.is_authenticated:
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user)
                return Response(serializer.data)
            return Response(serializer.errors)
        return Response({"error": "You must be logged in to create a post"})

    def put(self, request, pk=None):
        if pk:
            post = get_object_or_404(Post, pk=pk)
            if request.user == post.author:
                serializer = PostSerializer(post, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors)
            return Response({"error": "You do not have permission to edit this post"})
        return Response({"error": "Please provide a post ID in the URL eg.http://127.0.0.1:8000/posts/4"})

    def delete(self, request, pk=None):
        if pk:
            post = get_object_or_404(Post, pk=pk)
            if request.user == post.author:
                post.delete()
                return Response({"message": "Post deleted successfully"})
            return Response({"error": "You do not have permission to delete this post"})
        return Response({"error": "Please provide a post ID in the URL eg.http://127.0.0.1:8000/posts/4"})


# Comment APIView
class CommentViewSet(APIView):
# --------------------------------------------------------------- FOR PERMISSION ---------------------------------------------------------------
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, pk=None):
        if pk:
            comment = get_object_or_404(Comment, pk=pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        else:
            comments = Comment.objects.all()
# --------------------------------------------------------------- FOR SEARCH QUERY -------------------------------------------------------------
            search_query = request.query_param.get('search', None)
            if search_query:
                comments = comments.filter(Q(content__icontains=search_query) | Q(user__username__icontains=search_query) | Q(post__title__icontains=search_query))
# --------------------------------------------------------------- FOR PAGINATION ---------------------------------------------------------------
            paginator = PageNumberPagination()
            paginator.page_size = 2
            result_page = paginator.paginate_queryset(comments, request)
            serializer = CommentSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({"error": "You must be logged in to create a comment"})
        
        post_id = request.data.get('post_id')
        if not post_id:
            return Response({"error": "Post ID is required eg.{'post_id':4, 'content':'$COMMENT'}"})
        
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data)
        return Response(serializer.errors)

    def put(self, request, pk=None):
        if pk:
            comment = get_object_or_404(Comment, pk=pk)
            if request.user == comment.user:
                serializer = CommentSerializer(comment, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors)
            return Response({"error": "You do not have permission to edit this comment"})
        return Response({"error": "Please provide a comment ID in the URL eg. http://127.0.0.1:8000/comments/4"})

    def delete(self, request, pk=None):
        if pk:
            comment = get_object_or_404(Comment, pk=pk)
            if request.user == comment.user:
                comment.delete()
                return Response({"message": "Comment deleted successfully"})
            return Response({"error": "You do not have permission to delete this comment"})
        return Response({"error": "Please provide a comment ID in the URL eg. http://127.0.0.1:8000/comments/4"})

class RegisterUserView(APIView):
    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            email = request.data.get('email', '')

            if User.objects.filter(username=username).exists():
                return Response({"error": "Username already exists"})

            user = User.objects.create_user(username=username, password=password, email=email)
            return Response({"message": "User created successfully!", "user" : user} )
        except IntegrityError:
            return Response({"error": "A user with this email already exists."})
        except Exception as e:
            return Response({"error": str(e)})

