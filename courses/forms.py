from django import forms
from courses.models import Module



class ModuleForm(forms.ModelForm):
	class Meta:
		model = Module
		fields = ['name',]