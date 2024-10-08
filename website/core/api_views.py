from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .models import BlogModel
from .models import CommentModel, Follow, ProfileOfUser
from .serializers import CommentSerializer, FollowSerializer



class CommentCreateAPI(APIView):
    
    def post(self, request, blog_id):
        if not request.user.is_authenticated:
            return Response({'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        blog = get_object_or_404(BlogModel, pk=blog_id)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(blog=blog, user=request.user)
            return Response({'message': 'Comment created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Follou(APIView):
    def post(self, request, user_id):
        followed_user_profile = get_object_or_404(ProfileOfUser, user__id=user_id)
        follower = request.user
        
        serializer = FollowSerializer(data={'follower': follower.id, 'following': followed_user_profile.user.id})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Followed successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        following_user_profile = get_object_or_404(ProfileOfUser, user__id=user_id)
        follower = request.user

        follow_instance = Follow.objects.filter(
            follower=follower,
            following=following_user_profile.user
        ).first()
        
        if follow_instance:
            follow_instance.delete()
            return Response({'message': 'Successfully unfollowed the user.'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Not following this user.'}, status=status.HTTP_400_BAD_REQUEST)    