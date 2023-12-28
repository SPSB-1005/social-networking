from django.db import models
from django.contrib.auth.models import User


class Friend_Request(models.Model):
    sender = models.ForeignKey(User, related_name='sent_request', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name= 'received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'),('accepted', 'Accepted'),('rejected','Rejected')])
    timestamp = models.DateTimeField(auto_now_add=True)

