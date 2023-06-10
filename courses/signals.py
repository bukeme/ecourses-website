from django.db.models.signals import post_delete
from django.dispatch import receiver
from courses.models import Module, Lecture


@receiver(post_delete, sender=Module)
def reoder_module(sender, instance, *args, **kwargs):
	for index, obj in enumerate(Module.objects.filter(course=instance.course), start=1):
		obj.order = index
		obj.save()

@receiver(post_delete, sender=Lecture)
def reoder_lecture(sender, instance, *args, **kwargs):
	for index, obj in enumerate(Lecture.objects.filter(module=instance.module), start=1):
		obj.order = index
		obj.save()