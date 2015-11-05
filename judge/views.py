from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import hashlib, time

from django.contrib.auth.models import User
from .models import Coder, Problem, Entry
from .forms import SubmitForm, NewUserForm

# final_scores computes the overall composite scores for all of the active coders
def final_scores():
	submissions = Entry.objects.all().order_by("-score") # all submitted code in order of score
	coder_list = [] # will eventually contain all coder names
	coder_data = [] # list of dictionaries, each with key=problem and value=score
	# for every coder, if the coder is not in the list already, add him
	# then, if that coder hasn't submitted an entry for the problem, then add the score
	# otherwise, ignore the entry because the coder got more points in a previous entry
	for code in submissions:
		if not code.coder.user.username in coder_list:
			coder_list.append(code.coder.user.username)
			coder_data.append({})
		pos = coder_list.index(code.coder.user.username)
		if not code.problem.title in coder_data[pos]:
			coder_data[pos][code.problem.title] = float(code.score)
	raw_scores = [] # each is a coder's sum of scores
	max_score = 1 # maximum score of all coders, initially 1 to prevent dividing by zero
	for i in range(len(coder_list)):
		sum = 0
		for key in coder_data[i]:
			sum += coder_data[i][key]
		if max_score < sum:
			max_score = sum
		raw_scores.append(sum)
	unsorted_scores = [] # the composite scores will be somewhat of a percentile 
	for person in Coder.objects.all(): # add coders who haven't submitted anything
		if not person.user.username in coder_list:
			unsorted_scores.append({"name": person.user.username, "composite_score": 0.000})
	for i in range(len(coder_list)):
		unsorted_scores.append({"name": coder_list[i], "composite_score": round(100 * raw_scores[i] / max_score, 3)})
	final_scores = sorted(unsorted_scores, key = lambda k: k["composite_score"], reverse = True)
	for cnt in range(len(final_scores)):
		if cnt > 1 and final_scores[cnt]["composite_score"] == final_scores[cnt - 1]["composite_score"]:
			final_scores[cnt]["rank"] = final_scores[cnt - 1]["rank"]
		else:
			final_scores[cnt]["rank"] = cnt + 1
	for cnt in range(len(final_scores)): # save entry data to the Coder objects
		person = Coder.objects.filter(user__username = final_scores[cnt]["name"])[0]
		person.overall_rank = final_scores[cnt]["rank"]
		person.overall_score = final_scores[cnt]["composite_score"]
		person.save()
	return final_scores

# problem_scores returns the scores specific to a certain problem
def problem_scores(submissions):
	f_scores = []
	count = 1
	for code in submissions:
		if not any(code.coder.user.username in fs.values() for fs in f_scores):
			if ( len(f_scores) == 0 or code.score != f_scores[-1]["number"] ):
				f_scores.append({"rank": count, "name": code.coder.user.username, "number": code.score})
			else:
				f_scores.append({"rank": f_scores[-1]["rank"], "name": code.coder.user.username, "number": code.score})
			count += 1
	return f_scores

# IndexView dictates the homepage data
class IndexView(TemplateView):
	template_name = "judge/index.html"
	def get_context_data(self, **kwargs): 
		# coder_list contains list of coders in order of input
		# coder_data contains list of dictionaries corresponding to scores from users in coder_list
		context = super(IndexView, self).get_context_data(**kwargs)
		context["top_coders_list"] = final_scores()[:5]
		return context

# CodersView dictates the entries in the coders' leaderboard
class CodersView(TemplateView):
	template_name = "judge/coders.html"
	def get_context_data(self, **kwargs): 
		context = super(CodersView, self).get_context_data(**kwargs)
		context["final_scores"] = final_scores()
		context["current_user"] = self.request.user
		return context

# ProfileView dictates the information of a coder's profile
class ProfileView(generic.DetailView):
	model = User
	slug_field = "username"
	template_name = "judge/profile.html"
	def get_context_data(self, **kwargs): 
		f_scores = final_scores()
		context = super(ProfileView, self).get_context_data(**kwargs)
		context["current_user"] = self.request.user
		return context

# ProblemsView dictates the list of problems on the problems index page
class ProblemsView(generic.ListView):
	template_name = "judge/problems.html"
	context_object_name = "problems_list"
	def get_queryset(self):
		return Problem.objects.all()

# SubmitView dictates what the client sees upon viewing an individual problem's page 
class SubmitView(generic.DetailView):
	model = Problem
	template_name = "judge/submit.html"
	def get_context_data(self, **kwargs):
		context = super(SubmitView, self).get_context_data(**kwargs)
		context["submit_form"] = SubmitForm()
		return context
		
# LeaderboaardView dictates a problem's leaderboard
class LeaderboardView(generic.DetailView):
	model = Problem
	template_name = "judge/leaderboard.html"
	def get_context_data(self, **kwargs): 
		context = super(LeaderboardView, self).get_context_data(**kwargs)
		prob = context["problem"]
		submissions = prob.entry_set.all().order_by("-score")
		context["final_scores"] = problem_scores(submissions)
		context["current_user"] = self.request.user
		return context

# get_entry retrieves a user's form submission
def get_entry(request, problem_slug):
	prob = get_object_or_404(Problem, slug=problem_slug)
	name = request.user
	if request.method == "POST":
		form = SubmitForm(request.POST)
		if form.is_valid():
			source = form.cleaned_data["source"]
			time_key = hashlib.md5(unicode(timezone.now())).hexdigest()
			source_key = problem_slug + time_key
			request.session[source_key] = source
			return HttpResponseRedirect(reverse('judge:process', args=(prob.slug,source_key)))
		return render(request, "judge/submit.html", {
			"submit_form": form,
			"problem": prob,
			"error_message": "Please try again.",
		})
	else:
		form = SubmitForm()
		context = {"submit_form": form}
		return render(request, "judge/submit.html", context)

# process_entry retrieves the necessary fields for processing the submission request
def process_entry(request, problem_slug, source_key):
	prob = get_object_or_404(Problem, slug=problem_slug)
	if request.session.get(source_key, None):
		context = {
			"source_code": request.session.get(source_key, None), 
			"problem": prob,
			"user": request.user.coder,
			"post_url": reverse('judge:to_results', args=(prob.slug,source_key)),
			"compare_url": reverse('judge:compare', args=(prob.slug,source_key)),
			"leaderboard_url": reverse('judge:leaderboard', args=(prob.slug,))
		}
		return render(request, "judge/loading.html", context)
	else:
		raise Http404("Submission not found.")

# compare_answer compares the answer computed by the submission to the actual solution
def compare_answer(request, problem_slug, source_key):
	prob = get_object_or_404(Problem, slug=problem_slug)
	if request.method == "POST":
		output = request.POST.get('output')
		if output == prob.answer:
			data = { 'same': True }
			return JsonResponse(data)
		else:
			data = { 'same': False }
			return JsonResponse(data)
	data = { 'same': False }
	return JsonResponse(data)

# to_results dictates how the client sees the "successful submission" page followed by the leaderboard page
def to_results(request, problem_slug, source_key):
	prob = get_object_or_404(Problem, slug=problem_slug)
	if request.method == "POST":
		name = request.POST.get('submitter')
		score = int(request.POST.get('runtime'))
		source = request.POST.get('source')
		e = Entry(coder = Coder.objects.filter(user__username = name)[0], problem = prob, text = source, score = 5000 - score)
		e.save() # saving the code and attached information to an entry
		data = { 'score': score, 'entry_id': e.id }
		return JsonResponse(data) # returns a success message to redirect to leaderboard
	else:
		data = { 'score': -1 }
		return JsonResponse(data)

# entry_leaderboard dictates how the user sees the problem leaderboard
def entry_leaderboard(request, problem_slug, entry_id):
	prob = get_object_or_404(Problem, slug=problem_slug)
	context = { "problem": prob }
	context["entry"] = get_object_or_404(Entry, id=entry_id)
	submissions = prob.entry_set.all().order_by("-score")
	context["final_scores"] = problem_scores(submissions)
	context["current_user"] = request.user
	return render(request, "judge/leaderboard.html", context)

# NewUserView dictates the form that a new user attempting to register sees
class NewUserView(TemplateView):
	template_name = "judge/register.html"
	def get_context_data(self, **kwargs):
		context = super(NewUserView, self).get_context_data(**kwargs)
		context["user_form"] = NewUserForm()
		return context

# register_user collects the new user's account information and creates a coder account
def register_user(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data["name"]
			pwd1 = form.cleaned_data["pwd1"]
			pwd2 = form.cleaned_data["pwd2"]
			if pwd1 == pwd2:
				if not User.objects.filter(username = name):
					new_user = User.objects.create_user(username = name, password = pwd1)
					new_coder = Coder(user = new_user, overall_score = 0, overall_rank = 0)
					new_coder.save()
					return HttpResponseRedirect(reverse('judge:login'))
				else:
					return render(request, "judge/register.html", {
						"user_form": form,
						"error_message": "Username already in use.",
					})
			else:
				return render(request, "judge/register.html", {
					"user_form": form,
					"error_message": "Passwords do not match.",
				})
		else:
			return render(request, "judge/register.html", {
				"user_form": form,
				"error_message": "Please try again.",
			})

	else:
		form = NewUserForm()
		context = {"user_form": form}
		return render(request, "judge/register.html", context)




