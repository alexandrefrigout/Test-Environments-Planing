from django.contrib import admin
from Calendar.models import Application
from Calendar.models import Envs
from Calendar.models import Request

class RequestAdmin(admin.ModelAdmin):
	list_display = ('title', 'reference', 'start', 'end', 'get_apps' , 'version')
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = ('env')
		return super(RequestAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Application)
admin.site.register(Request, RequestAdmin)
admin.site.register(Envs)
