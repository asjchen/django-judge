from django.core.urlresolvers import reverse

def auth_status(request):
	if not request.user.is_authenticated():
		return {'display': "Login", 'profile_link': 'judge:login', 'log_link': 'judge:login' }
	else:
		return {'display': "Logout", 'profile_link': 'judge:profile', 'current': request.user.username, 'log_link': 'judge:logout' }