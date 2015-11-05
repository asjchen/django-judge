from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
	url(r'^$', views.IndexView.as_view(), name = 'index'),

# The following few views are specifically for account handling
	url(r'^account/login/$', "django.contrib.auth.views.login", name = 'login'),
	url(r'^account/logout/$', "django.contrib.auth.views.logout", {"next_page": "/judge/"}, name = 'logout'),
	url(r'^account/password_change/$', "django.contrib.auth.views.password_change", {"post_change_redirect": "/judge/"}, name = 'password_change'),
	url(r'^account/register/$', views.NewUserView.as_view(), name = 'register'),
	url(r'^account/register/make/$', views.register_user, name = 'make_user'),

	url(r'^coders/$', views.CodersView.as_view(), name = 'coders'),
	url(r'^coders/(?P<slug>.*)/$', views.ProfileView.as_view(), name = 'profile'),
	url(r'^problems/$', views.ProblemsView.as_view(), name = 'problems'),
	url(r'^problems/(?P<slug>([^/]*))/$', login_required(views.SubmitView.as_view(), login_url="/judge/account/login/"), name = 'submit'),
	url(r'^problems/(?P<problem_slug>([^/]*))/send/$', login_required(views.get_entry, login_url="judge/account/login/"), name = 'send'),
	url(r'^problems/(?P<slug>([^/]*))/leaderboard/$', views.LeaderboardView.as_view(), name = 'leaderboard'),
	url(r'^problems/(?P<problem_slug>([^/]*))/leaderboard/(?P<entry_id>([^/]*))/$', views.entry_leaderboard, name = 'entry_leaderboard'),
	
# Upon submission of a problem, the client sees these pages in order
	url(r'^problems/(?P<problem_slug>([^/]*))/(?P<source_key>([^/]*))/$', views.process_entry, name = 'process'),
	url(r'^problems/(?P<problem_slug>([^/]*))/(?P<source_key>([^/]*))/compare/$', views.compare_answer, name = 'compare'),
	url(r'^problems/(?P<problem_slug>([^/]*))/(?P<source_key>([^/]*))/to-results/$', views.to_results, name = 'to_results'),

]
