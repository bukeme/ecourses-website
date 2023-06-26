from django import template
from purchase.models import Notification


register = template.Library()

@register.simple_tag
def notification_count(recipient):
	if recipient.is_authenticated:
		return Notification.objects.filter(recipient=recipient, read=False).count()
	return None