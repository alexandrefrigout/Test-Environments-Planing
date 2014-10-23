from django.db import models


class Application(models.Model):
	appname = models.CharField(max_length=30)

	def __unicode__(self):
		return self.appname

	class Meta:
        	ordering = ('appname',)
		
#Each Envs instance will contain all available applications in the related env
class Envs(models.Model):
    	name = models.CharField(max_length=10)
	applications = models.ManyToManyField(Application)

	def __unicode__(self):
		return self.name

	class Meta:
		ordering = ('name',)

VER_CHOICES = (
        ('Prod', 'prod'),
        ('Release', 'release'),
)

class Request(models.Model):
	Prod = 'Prod'
	Release = 'Release'
	VER_CHOICES = (
	        (Prod, 'Prod'),
        	(Release, 'Release'),
	)
	date_creation = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=200)
	reference = models.CharField(max_length=50)
	start = models.DateField()
	end = models.DateField()
	version = models.CharField(max_length=10, choices=VER_CHOICES, default=Prod)
	refresh = models.BooleanField()
	daterefresh = models.DateField(null = True, blank = True)
	batchs = models.BooleanField()
	apps = models.ManyToManyField('Application')
	env = models.ForeignKey(Envs, null=True,blank=True)
	comments = models.TextField()

	def __unicode__(self):
		return self.title

	def get_apps(self):
		return ", ".join([p.appname for p in self.apps.all()])

	class Meta:
		ordering = ('-date_creation',)
