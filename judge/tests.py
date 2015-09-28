import unittest, time
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User
from .models import Coder, Problem, Entry
from .forms import SubmitForm


def create_user(username, password):
	return User.objects.create(username = username, password = password)

def create_coder(user, overall_score, overall_rank):
	return Coder.objects.create(user = user, overall_score = overall_score, overall_rank = overall_rank)

def create_problem(title, statement, slug, answer, arg_vars, arg_values):
	return Problem.objects.create(title = title, statement = statement, slug = slug, answer = answer, arg_vars = arg_vars, arg_values = arg_values)

def create_entry(coder, problem, text, score):
	return Entry.objects.create(coder = coder, problem = problem, text = text, score = score)

class GenericModelTests(TestCase):
	def test_coder_can_access_entries_problem(self):
		user_test = create_user("foo", "foo")
		coder_test = create_coder(user_test, 1.0, 1)
		problem_test = create_problem("Success", "", "", "", "", "")
		entry_test = create_entry(coder_test, problem_test, "", 1)
		correct_entry = coder_test.entry_set.get()
		self.assertEqual(correct_entry.problem.title, "Success")

class LeaderboardViewTests(TestCase):

	def test_leaderboard_index_view_with_no_coders(self):
		user_test = create_user("foo", "foo")
		coder_test = create_coder(user_test, 99.0, 1)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		response = self.client.get(reverse("judge:leaderboard", args=("slug",)))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Leaderboard")
		self.assertContains(response, problem_test.title)
		self.assertContains(response, "No users yet.")
		self.assertQuerysetEqual(response.context["final_scores"], [])
	
	# Many of the user, coder, entry, and problem constructions are unique to their corresponding test, but this covers several non-special case tests
	def make_objects(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 99.0, 1)
		user2 = create_user("user2", "foo")
		coder2 = create_coder(user2, 75.0, 2)
		user3 = create_user("user3", "foo")
		coder3 = create_coder(user3, 50.0, 3)
		user4 = create_user("user4", "foo")
		coder4 = create_coder(user4, 25.0, 4)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		entry1 = create_entry(coder1, problem_test, "", 99)
		entry2 = create_entry(coder2, problem_test, "", 75)
		entry3 = create_entry(coder3, problem_test, "", 50)
		entry4 = create_entry(coder4, problem_test, "", 25)

	def test_problem_leaderboard_ranks_increase(self):
		self.make_objects()
		response = self.client.get(reverse("judge:leaderboard", args=("slug",)))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Leaderboard")
		self.assertContains(response, "Title")
		scores = response.context["final_scores"]
		valid = True
		for it in range(1, len(scores)):
			if scores[it]["rank"] < scores[it - 1]["rank"]:
				valid = False
		self.assertEqual(valid, True)

	def test_problem_leaderboard_scores_decrease(self):
		self.make_objects()
		response = self.client.get(reverse("judge:leaderboard", args=("slug",)))
		scores = response.context["final_scores"]
		valid = True
		for it in range(1, len(scores)):
			if scores[it]["number"] > scores[it - 1]["number"]:
				valid = False
		self.assertEqual(valid, True)

	def test_problem_leaderboard_no_name_duplicates(self):
		self.make_objects()
		coder1 = Coder.objects.get(user__username = "user1")
		problem_test = Problem.objects.get(slug = "slug")
		entry5 = create_entry(coder1, problem_test, "", 89)
		response = self.client.get(reverse("judge:leaderboard", args=("slug",)))
		scores = response.context["final_scores"]
		valid = True
		for it in range(1, len(scores)):
			if scores[it]["name"] == scores[it - 1]["name"]:
				valid = False
		self.assertEqual(valid, True)

	def test_only_highest_scores_used(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 99.0, 1)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		entry1 = create_entry(coder1, problem_test, "", 99)
		entry2 = create_entry(coder1, problem_test, "", 75)
		response = self.client.get(reverse("judge:leaderboard", args=("slug",)))
		scores = response.context["final_scores"]
		self.assertEqual(scores[0]["number"], 99.0)

	def test_same_scores_same_ranks(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 99.0, 1)
		user2 = create_user("user2", "foo")
		coder2 = create_coder(user2, 98.0, 2)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		entry1 = create_entry(coder1, problem_test, "", 50)
		entry2 = create_entry(coder2, problem_test, "", 50)
		response = self.client.get(reverse("judge:leaderboard", args=("slug",)))
		scores = response.context["final_scores"]
		self.assertEqual(scores[0]["rank"], scores[1]["rank"])

	def test_only_given_problem_contributes_to_leaderboard(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 99.0, 1)
		problem1 = create_problem("Title1", "", "slug1", "", "", "")
		problem2 = create_problem("Title2", "", "slug2", "", "", "")
		entry1 = create_entry(coder1, problem1, "", 50)
		entry2 = create_entry(coder1, problem2, "", 50)
		response = self.client.get(reverse("judge:leaderboard", args=("slug1",)))
		scores = response.context["final_scores"]
		self.assertEqual(len(scores), 1)

class ProblemsViewTests(TestCase):
	def test_problems_list_with_no_problems(self):
		response = self.client.get(reverse("judge:problems"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Problems")
		self.assertContains(response, "No problems yet.")

class CodersViewTests(TestCase):
	def test_coders_list_with_no_coders(self):
		response = self.client.get(reverse("judge:coders"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Not enough users yet.")

	def make_objects(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 100.0, 1)
		user2 = create_user("user2", "foo")
		coder2 = create_coder(user2, 75.0, 2)
		user3 = create_user("user3", "foo")
		coder3 = create_coder(user3, 50.0, 3)
		user4 = create_user("user4", "foo")
		coder4 = create_coder(user4, 25.0, 4)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		entry1 = create_entry(coder1, problem_test, "", 100)
		entry2 = create_entry(coder2, problem_test, "", 75)
		entry3 = create_entry(coder3, problem_test, "", 50)
		entry4 = create_entry(coder4, problem_test, "", 25)

	def test_coders_list_basic_score_evaluation(self):
		self.make_objects()
		coder1 = Coder.objects.get(user__username = "user1")
		entry4 = Entry.objects.get(score = 25)
		entry4.coder = coder1
		entry4.save()
		coder4 = Coder.objects.get(user__username = "user4")
		coder4.delete()
		response = self.client.get(reverse("judge:coders"))
		scores = response.context["final_scores"]
		self.assertEqual(scores[0]["rank"], 1)
		self.assertEqual(scores[0]["name"], "user1")
		self.assertEqual(scores[0]["composite_score"], 100.000)
		self.assertEqual(scores[1]["rank"], 2)
		self.assertEqual(scores[1]["name"], "user2")
		self.assertEqual(scores[1]["composite_score"], 75.000)
		self.assertEqual(scores[2]["rank"], 3)
		self.assertEqual(scores[2]["name"], "user3")
		self.assertEqual(scores[2]["composite_score"], 50.000)

	def test_coders_list_ranks_increase(self):
		self.make_objects()
		response = self.client.get(reverse("judge:coders"))
		scores = response.context["final_scores"]
		valid = True
		for it in range(1, len(scores)):
			if scores[it]["rank"] < scores[it - 1]["rank"]:
				valid = False
		self.assertEqual(valid, True)

	def test_coders_list_scores_decrease(self):
		self.make_objects()
		response = self.client.get(reverse("judge:coders"))
		scores = response.context["final_scores"]
		valid = True
		for it in range(1, len(scores)):
			if scores[it]["composite_score"] > scores[it - 1]["composite_score"]:
				valid = False
		self.assertEqual(valid, True)

	def test_new_user_end_of_list(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 99.0, 1)
		user2 = create_user("user2", "foo")
		coder2 = create_coder(user2, 99.0, 2)
		user3 = create_user("user3", "foo")
		coder3 = create_coder(user3, 99.0, 3)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		entry1 = create_entry(coder1, problem_test, "", 99)
		entry2 = create_entry(coder2, problem_test, "", 75)
		entry3 = create_entry(coder3, problem_test, "", 50)
		user4 = create_user("user4", "foo")
		coder4 = create_coder(user4, 99.0, 4)
		response = self.client.get(reverse("judge:coders"))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["final_scores"][-1]["name"], "user4")

	def test_coders_list_no_duplicates(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 99.0, 1)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		entry1 = create_entry(coder1, problem_test, "", 99)
		entry2 = create_entry(coder1, problem_test, "", 75)
		entry3 = create_entry(coder1, problem_test, "", 50)
		entry4 = create_entry(coder1, problem_test, "", 25)
		response = self.client.get(reverse("judge:coders"))
		scores = response.context["final_scores"]
		self.assertEqual(len(scores), 1)


class ProfileViewTests(TestCase):
	def test_basic_profile(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 100.000, 1)
		problem_test = create_problem("Title", "", "slug", "", "", "")
		entry1 = create_entry(coder1, problem_test, "", 99)
		response = self.client.get(reverse("judge:profile", args=("user1",)))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "user1")
		self.assertContains(response, 100.000)
		self.assertContains(response, 1)

class IndexViewTests(TestCase):
	def test_index_list_with_no_coders(self):
		response = self.client.get(reverse("judge:index"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Not enough users yet.")

	def test_index_list_max_size_five(self):
		user1 = create_user("user1", "foo")
		coder1 = create_coder(user1, 99.0, 1)
		user2 = create_user("user2", "foo")
		coder2 = create_coder(user2, 98.0, 2)
		user3 = create_user("user3", "foo")
		coder3 = create_coder(user3, 97.0, 3)
		user4 = create_user("user4", "foo")
		coder4 = create_coder(user4, 96.0, 4)
		user5 = create_user("user5", "foo")
		coder5 = create_coder(user5, 95.0, 5)
		user6 = create_user("user6", "foo")
		coder6 = create_coder(user6, 95.0, 5)
		response = self.client.get(reverse("judge:index"))
		self.assertEqual(response.status_code, 200)
		top_coders = response.context["top_coders_list"]
		self.assertEqual(len(top_coders), 5)
		

class SubmitViewTests(TestCase):

	def setUp(self):
		self.client = Client()
		user_test = create_user("user1", "foo")
		user_test.set_password("foo")
		user_test.save()
		user1 = authenticate(username='user1', password='foo')
		login_successful = self.client.login(username="user1", password="foo")
		prob = create_problem("Title", "Answer me.", "slug", "answer", "n1, n2", "42 42")

	def test_problem_properties_shown(self):
		response = self.client.get(reverse("judge:submit", args=("slug",)))
		self.assertContains(response, "Title")
		self.assertContains(response, "Answer me.")
		self.assertContains(response, "n1, n2")

	def test_form_validity(self):
		form_data = {"source": "code"}
		form = SubmitForm(data = form_data)
		self.assertTrue(form.is_valid())

	def test_form_with_empty_text(self):
		form_data = {"source": ""}
		form = SubmitForm(data = form_data)
		self.assertEquals(form.errors["source"], [u"This field is required."])


class AuthenticationTests(TestCase):

	def setUp(self):
		self.client = Client()
		user_test = create_user("user1", "foo")

	def test_login_incorrect_creds(self):
		user1 = User.objects.get(username = "user1")
		user1.set_password("password")
		user1.save()
		user1 = authenticate(username='user1', password='foo')
		login_successful = self.client.login(username="user1", password="foo")
		self.assertEqual(login_successful, False)

	def test_login_correct_creds(self):
		user1 = User.objects.get(username = "user1")
		user1.set_password("foo")
		user1.save()
		user1 = authenticate(username='user1', password='foo')
		login_successful = self.client.login(username="user1", password="foo")
		self.assertEqual(login_successful, True)

	def test_logout_goes_to_index(self):
		user1 = User.objects.get(username = "user1")
		user1.set_password("password")
		user1.save()
		user1 = authenticate(username='user1', password='foo')
		login_successful = self.client.login(username="user1", password="foo")
		self.client.logout()
		response = self.client.get(reverse("judge:logout"))
		self.assertRedirects(response, reverse("judge:index"))

	def test_restrict_access_to_submit(self):
		create_problem("", "", "slug", "", "", "")
		response = self.client.get(reverse("judge:submit", args=("slug",)))
		self.assertRedirects(response, reverse("judge:login") + "?next=" + reverse("judge:submit", args=("slug",)))

	def test_create_existing_coder_fails(self):
		response = self.client.post(reverse('judge:make_user'), {'name': "user1", 'pwd1': "password", 'pwd2': "password"})
		self.assertContains(response, "Username already in use.")

	def test_create_coder_with_diff_pwds(self):
		response = self.client.post(reverse('judge:make_user'), {'name': "user2", 'pwd1': "password1", 'pwd2': "password"})
		self.assertContains(response, "Passwords do not match.")

	def test_create_coder_succesfully(self):
		response = self.client.post(reverse('judge:make_user'), {'name': "user2", 'pwd1': "password", 'pwd2': "password"})
		self.assertRedirects(response, reverse("judge:login"))
		self.assertTrue(User.objects.filter(username = "user2"))

class ProcessEntryTests(TestCase):
	def setUp(self):
		self.client = Client()
		user_test = create_user("user1", "foo")
		user_test.set_password("foo")
		user_test.save()
		user1 = authenticate(username='user1', password='foo')
		login_successful = self.client.login(username="user1", password="foo")
		coder_test = create_coder(user_test, 0, 0)
		prob = create_problem("Add", "Answer me.", "slug", "84", "n1, n2", "42 42")

	def test_submitted_code_saved_as_entry(self):
		response = self.client.post(reverse('judge:to_results', args=("slug","slugsourcekey")), {'submitter': "user1", 'runtime': "1000", 'source': "return n1 + n2;"})
		self.assertTrue(Entry.objects.filter(text = "return n1 + n2;", problem__slug = "slug", coder__user__username = "user1"))


