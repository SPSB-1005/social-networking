# Create your views here.
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from .models import User,Friend_Request
from .serializers import UserSerializer,FriendRequestSerializer
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache



class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        
        user = User.objects.filter(email=email).first()
        if user:
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response(token, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 10

    def get_queryset(self):
        search_keyword = self.request.GET.get('search', '')

        # Search users by email or name
        current_user = self.request.user

        queryset = User.objects.filter(
            Q(username__icontains=search_keyword)| Q(email__icontains=search_keyword)
        )
        return queryset

class FriendRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        action = request.data.get('action')
        user_id = request.data.get('user_id')

        if action == 'send':
            return self.send_request(request.user, user_id)
        elif action == 'accept':
            return self.accept_request(request.user, user_id)
        elif action == 'reject':
            return self.reject_request(request.user, user_id)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    def send_request(self, sender, receiver_id):
        cache_key = f'friend-requests-sent-{sender.id}'
        current_count = cache.get(cache_key, 0)

        if current_count >= 3:
                return Response({"error": "Rate limit exceeded. Maximum 3 requests per minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        receiver = User.objects.get(pk=receiver_id)
        if Friend_Request.objects.filter(sender=sender, receiver=receiver).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        Friend_Request.objects.create(sender=sender, receiver=receiver, status='pending')

        timeout = 60 
        if current_count:
            cache.incr(cache_key)
        else:
            cache.set(cache_key, 1, timeout=timeout)

        return Response({'status': 'Friend request sent'}, status=status.HTTP_201_CREATED)

    def accept_request(self, receiver, sender_id):

        friend_request = Friend_Request.objects.filter(sender_id=sender_id, receiver=receiver, status='pending').first()
        if not friend_request:
            return Response({'error':'No such friend request exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.status = 'accepted'
        friend_request.save()
        return Response({'status': 'Friend request accepted'}, status=status.HTTP_200_OK)

    def reject_request(self, receiver, sender_id):

        friend_request = Friend_Request.objects.get(sender_id=sender_id, receiver=receiver, status='pending')
        friend_request.status = 'rejected'
        friend_request.save()
        return Response({'status': 'Friend request rejected'}, status=status.HTTP_200_OK)
    

class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all accepted friend requests where the user is either the sender or the receiver
        friend_requests = Friend_Request.objects.filter(
            Q(sender=user, status='accepted') | Q(receiver=user, status='accepted')
        )

        # Extract the IDs of all friends
        friend_ids = set()
        for fr in friend_requests:
            friend_ids.add(fr.receiver.id if fr.sender == user else fr.sender.id)

        # Query the User model for all friends
        return User.objects.filter(id__in=friend_ids)
       

class ListPendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all pending friend requests where the user is the receiver
        return Friend_Request.objects.filter(receiver=user, status='pending')
