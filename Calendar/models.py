#-*- coding: utf-8 -*-
from django.db import models
import datetime


class Application(models.Model):
	appname = models.CharField(max_length=30, unique=True)

	def __unicode__(self):
		return self.appname

        def get_appname(self):
                return self.appname

	class Meta:
        	ordering = ('appname',)
		
#Each Envs instance will contain all available applications in the related env
class Envs(models.Model):
    	name = models.CharField(max_length=10, unique=True)
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
	#Version des programmes et de la copie de la db
	Prod = 'Prod'
	Release = 'Release'
	VER_CHOICES = (
	        (Prod, 'Prod'),
        	(Release, 'Release'),
	)

	#types de batche a tourner
	NoBatchs = 'Aucun'
	Daily = 'Journalier'
	OnDemand = 'A la demande'
	BATCH_CHOICES = (
		(NoBatchs, 'Aucun'),
		(Daily, 'Journalier'),
		(OnDemand, 'A la demande'),
	)	

	date_creation = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=200)
	reference = models.CharField(max_length=50)
	trigram = models.CharField(max_length=3)
	start = models.DateField()
	end = models.DateField()
	version = models.CharField(max_length=10, choices=VER_CHOICES, default=Prod)
	refresh = models.BooleanField()
	daterefresh = models.DateField(null=True, blank=True)
	batchs = models.BooleanField()
	batchType = models.CharField(max_length=15, choices=BATCH_CHOICES, default=NoBatchs)
	apps = models.ManyToManyField('Application')
	env = models.ForeignKey(Envs, null=True,blank=True)
	comments = models.TextField()

	def __unicode__(self):
		return self.title

	def get_apps(self):
		return ", ".join([p.appname for p in self.apps.all()])

	class Meta:
		ordering = ('-date_creation',)

class History(models.Model):
	request = models.ForeignKey('Request')
	datemodif = models.DateTimeField(auto_now_add=True, auto_now=True)
	fieldmodified = models.CharField(max_length=50)
	valuebefore = models.TextField()
	valueafter = models.TextField()

	class Meta:
		ordering = ('-datemodif',)
