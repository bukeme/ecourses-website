from django.db.models.signals import post_delete
from django.dispatch import receiver
from courses.models import Module


@receiver(post_delete, sender=Module)
def reoder_module(sender, *args, **kwargs):
	for index, obj in enumerate(Module.objects.all(), start=1):
		print(index)
		obj.order = index
		obj.save()