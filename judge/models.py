from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class Coder(models.Model):
	user = models.OneToOneField(User)
	overall_rank = models.IntegerField(default = 0)
	overall_score = models.DecimalField(max_digits = 6, decimal_places = 3)
	def __unicode__(self):
		return self.user.username

class Problem(models.Model):
	title = models.CharField(max_length = 200)
	statement = models.TextField()
	slug = models.SlugField()
	answer = models.TextField()
	arg_vars = models.CharField(max_length = 200, default = "") # of form "n1, n2, n3"
	arg_values = models.CharField(max_length = 200, default = "") # of form "3, 4, 5"
	def __unicode__(self):
		return self.title

class Entry(models.Model):
	coder = models.ForeignKey(Coder)
	problem = models.ForeignKey(Problem)
	text = models.TextField()
	score = models.IntegerField(default = 0)
	def __unicode__(self):
		return self.coder.user.username + ': ' + self.problem.title



