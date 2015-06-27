from django import forms

from .models import Problem, Coder, Entry

class SubmitForm(forms.Form):
	source = forms.CharField(label = "Source Code", widget = forms.Textarea)

class NewUserForm(forms.Form):
	name = forms.CharField(label = "Username", widget = forms.TextInput)
	pwd1 = forms.CharField(label = "Password", widget = forms.PasswordInput)
	pwd2 = forms.CharField(label = "Confirm Password", widget = forms.PasswordInput)
	
