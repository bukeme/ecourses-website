from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='profile_image/%Y-%m-%d', default='profile_image/placeholder.jpg')
	headline = models.CharField(max_length=300, null=True, blank=True)
	overview = models.TextField(null=True, blank=True)

	@property
	def full_name(self):
		return f'{self.user.first_name} {self.user.last_name}'

	def __str__(self):
		return self.full_name
