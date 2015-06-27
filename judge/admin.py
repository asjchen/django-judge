from django.contrib import admin

from .models import Coder, Problem, Entry

admin.site.register(Coder)
admin.site.register(Problem)
admin.site.register(Entry)
