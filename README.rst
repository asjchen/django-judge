===========================================================
 The Arena - created by Andy Chen, guided by Zach Lovelady
===========================================================

The Arena is a simple online judge where users can submit Javascript code to solve algorithmic-based problems. Coders attempt to solve the test case(s) for each problem in the fastest time possible. Their results are compiled and presented in problem-specific and overall leaderboards.

Documentation is to appear in django-polls/docs.

===========================================================

To Get Started (it is recommended that this be run in virtualenv):

1) Add “judge” to your INSTALLED_APPS setting in settings.py

2) Include the judge URLconf in your project’s urls.py:
	url(r’^judge/‘, include(‘judge.urls’)),

3) Run ‘python manage.py migrate’ to create the judge models

4) Start the development server (with ‘python manage.py runserver’). The web administrator site can be accessed at http://127.0.0.1:8000/admin/ and the site itself can be seen at http://127.0.0.1:8000/judge/

