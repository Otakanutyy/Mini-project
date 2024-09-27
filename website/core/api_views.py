from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .models import BlogModel, LikeModel
from .models import CommentModel
from .serializers import CommentSerializer



class CommentCreateAPI(APIView):
    
    def post(self, request, blog_id):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the associated blog
        blog = get_object_or_404(BlogModel, pk=blog_id)

        # Create a Comment instance
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(blog=blog, user=request.user)
            return Response({'message': 'Comment created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
