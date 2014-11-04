#-*- coding: utf-8 -*- 
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import send_mail
import time
from datetime import date
from datetime import datetime
import datetime
import collections
import re
from Calendar.models import Envs, Application, Request, History

Informed_group='aef@ubp.ch'

class RequestFormAssign(forms.ModelForm):
        #Conserver la propriete required = false de daterefresh
        def __init__(self, *args, **kwargs):
                super(RequestFormAssign, self).__init__(*args, **kwargs)
                self.fields['daterefresh'].required = False
                self.fields['comments'].required = False

        start = forms.DateField(('%m/%d/%Y',), label='Debut', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateFrom'}))
        end = forms.DateField(('%m/%d/%Y',), label='Fin', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateTo'}))
        daterefresh = forms.DateField(('%m/%d/%Y',), label='Date du refresh', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateRefresh'}))

	def clean_end(self):
                cleaned_data = self.cleaned_data
                start = cleaned_data.get('start')
                end = cleaned_data.get('end')
                if end < start:
                        raise forms.ValidationError("La date de debut doit etre inferieure a la date de fin")
                return cleaned_data['end']

        def clean_daterefresh(self):
                cleaned_data = self.cleaned_data
                if cleaned_data.get('refresh') == True:
                        if not cleaned_data.get('daterefresh'):
                                raise forms.ValidationError("Veuillez preciser la date du refresh souhaite")
           	return cleaned_data['daterefresh']



        class Meta:
                model = Request


class RequestForm(forms.ModelForm):
	#Conserver la propriete required = false de daterefresh
	def __init__(self, *args, **kwargs):
		super(RequestForm, self).__init__(*args, **kwargs)
		self.fields['daterefresh'].required = False
		self.fields['comments'].required = False

	title = forms.CharField(label='Titre', widget=forms.TextInput(attrs={'id': 'reqtitle'}))
        trigram = forms.CharField(label='Trigramme', widget=forms.TextInput())
        refresh = forms.BooleanField(label='Besoin de refresh')
        batchs = forms.BooleanField(label='Besoin de batchs')
        batchType = forms.CharField(label='Type de batchs', widget=forms.TextInput())
        apps = forms.CharField(label='Applications', widget=forms.TextInput())
        comments = forms.CharField(label='Commentaires', widget=forms.TextInput())

	start = forms.DateField(('%m/%d/%Y',), label='Debut', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateFrom'}))
	end = forms.DateField(('%m/%d/%Y',), label='Fin', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateTo'}))
	daterefresh = forms.DateField(('%m/%d/%Y',), label='Date du refresh', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateRefresh'}))

	def clean_start(self):
		cleaned_data = self.cleaned_data
                start = cleaned_data.get('start')
		if start < datetime.datetime.now().date():
			raise forms.ValidationError("La date de debut doit etre superieure a la date courante")	
		return cleaned_data['start']

	def clean_end(self):
		cleaned_data = self.cleaned_data
		end = cleaned_data.get('end')
		start = cleaned_data.get('start')
		if end and start:
			if end < start:
				raise forms.ValidationError("La date de debut doit etre inferieure a la date de fin")	
		return cleaned_data['end']
	

	def clean_daterefresh(self):
		cleaned_data = self.cleaned_data
		if cleaned_data.get('refresh') == True:
			if not cleaned_data.get('daterefresh'):
				raise forms.ValidationError("Veuillez preciser la date du refresh souhaite")
		return cleaned_data['daterefresh']

		
	class Meta:
		model = Request
		exclude = ['env']

class RequestFormEdit(forms.ModelForm):
        #Conserver la propriete required = false de daterefresh
        def __init__(self, *args, **kwargs):
                super(RequestFormEdit, self).__init__(*args, **kwargs)
                self.fields['daterefresh'].required = False
                self.fields['comments'].required = False

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



        title = forms.CharField(label='Titre', widget=forms.TextInput(attrs={'id': 'reqtitle'}))
        trigram = forms.CharField(label='Trigramme', widget=forms.TextInput())
        comments = forms.CharField(label='Commentaires', widget=forms.Textarea())
	batchType = forms.ChoiceField(label='Type de batchs', choices=BATCH_CHOICES)
	version = forms.ChoiceField(label='Version des programmes et db', choices=VER_CHOICES)

        start = forms.DateField(('%m/%d/%Y',), label='Debut', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateFrom'}))
        end = forms.DateField(('%m/%d/%Y',), label='Fin', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateTo'}))
        daterefresh = forms.DateField(('%m/%d/%Y',), label='Date du refresh', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'dateRefresh'}))

        def clean_end(self):
                cleaned_data = self.cleaned_data
                end = cleaned_data.get('end')
                start = cleaned_data.get('start')
                if end and start:
                        if end < start:
                                raise forms.ValidationError("La date de debut doit etre inferieure a la date de fin")
                return cleaned_data['end']


        def clean_daterefresh(self):
                cleaned_data = self.cleaned_data
                if cleaned_data.get('refresh') == True:
                        if not cleaned_data.get('daterefresh'):
                                raise forms.ValidationError("Veuillez preciser la date du refresh souhaite")
                return cleaned_data['daterefresh']

	def clean_batchType(self):
		cleaned_data = self.cleaned_data
		if cleaned_data.get('batchs') == False:
			cleaned_data['batchType'] = 'Aucun'
		return cleaned_data['batchType']


        class Meta:
                model = Request
                exclude = ['env']



def create(request):
	"""
	La fonction create recupere les donnees du formulaire, cree une instance de Request et la sauve dans la db.
	A l'ouverture de la page, le formulaire vide est cree par le passage dans le else: form = RequestForm()
	Lorsque le formulaire est rempli et le bouton Sauvegarder presse, l'instance de Request est cree puis sauvegardee dans la db si le formulaire est valide.
	"""
	if request.method == 'POST':
		form = RequestForm(request.POST)
		if form.is_valid():
			form.save()
			req = Request.objects.get(title=request.POST['title'])
			applist = req.get_apps()
			message = "Bonjour, vous avez envoye une demande d'environnement de test pour le sujet " + request.POST['title'] + ".\nVotre demande est la suivante :\n\tReference : " + request.POST['reference'] + "i\n\t Date de debut : " +request.POST['start'] + "\n\tDate de fin : " +request.POST['end']+ "\n\tVersion des programmes et DB : " + request.POST['version'] + "\n\tDate des donnees souhaitee : " +request.POST['daterefresh'] + "\n\tTypes de batchs : " +request.POST['batchType'] + "\n\tApplications necessaires : " + applist + "\n\nCette requete sera prise en compte par l'equipe Environnement Management dans les plus brefs delais."
			send_mail("Demande d'environnement de test pour "+request.POST['title'], message, Informed_group, [request.POST['trigram']+'@ubp.ch'], fail_silently=False)
			return HttpResponseRedirect('/')
		else:
			print form.errors
	else:
		form = RequestForm()
	return render(request, 'Calendar/createreq.html', {'form' : form})

def returnApps(list):
	"""
	Retourne la liste des applications a partir d'une liste de QuerySet.
	"""
	applist = []
	for l in list:
		app = Application.objects.filter(id=l)
		applist.append(app[0].get_appname())
	return applist

def editRequest(request, title):
	"""
	La fonction editRequest cree un formulaire a partir de l'instance de Request que l'on veut editer.
	Lorsque les modifications sont faites, la demande est sauvegardee.
	"""
	tomodif = Request.objects.get(id=title)
	if request.method == 'POST':
		form = RequestFormEdit(request.POST, instance=tomodif)	
		if form.has_changed:
			changes = []
			for changed in form.changed_data:
				if changed == 'apps':
					modif = changed + " avant " + tomodif.get_apps() + " apres " + ", ".join(returnApps(form[changed].value()))
					changes.append(modif)
					change = History.objects.create(request = tomodif, fieldmodified=changed, valuebefore=tomodif.get_apps(), valueafter = ", ".join(returnApps(form[changed].value())))
				elif changed == 'start' or changed == 'end' or changed == 'daterefresh':
					modif = changed + " avant " + str(getattr(tomodif, changed)) + " apres " + str(form[changed].value())
                                        changes.append(modif)
                                        change = History.objects.create(request = tomodif, fieldmodified=changed, valuebefore=getattr(tomodif, changed), valueafter = datetime.datetime.strptime(form[changed].value(), "%m/%d/%Y").date())
				else:
					modif = changed + " avant " + str(getattr(tomodif, changed)) + " apres " + str(form[changed].value())
                                        changes.append(modif)
                                        change = History.objects.create(request = tomodif, fieldmodified=changed, valuebefore=getattr(tomodif, changed), valueafter = form[changed].value())

			message = "La demande "+request.POST['title']+" a ete modifiee.\nLes modifications sont les suivantes :\n" + "\n".join(changes)
			
			if form.is_valid():
                	        form.save()
				send_mail("Modification de la demande "+request.POST['title'], message, Informed_group, [request.POST['trigram']+'@ubp.ch'], fail_silently=False)
                	        return HttpResponseRedirect('/')
	else:
                form = RequestFormEdit(instance=tomodif)
        return render(request, 'Calendar/edit.html', {'form' : form})

def viewRequest(request, title):
	toview = Request.objects.get(id=title)
	form = RequestForm(instance=toview)
	applist = toview.get_apps()
	changelist = History.objects.filter(request=title)
	return render(request, 'Calendar/viewreq.html', {'form' : form, 'applis' : applist, 'history' : changelist})
	

def deleteRequest(request, title):
	todel = Request.objects.get(id=title)
	todel.delete()
	return HttpResponseRedirect('/')

def index(request):
	form = InputDateForm()
	all_req = Request.objects.order_by('-date_creation')[:]
	return render(request, 'Calendar/index.html', {'list_req' : all_req, 'form' : form})

@login_required
def assign(request, title):
	toassign = Request.objects.get(id=title)
        if request.method == 'POST':
                form = RequestFormAssign(request.POST, instance=toassign)
                if form.is_valid():
                        form.save()
			print "form saved"
			print toassign.env.name
                        return HttpResponseRedirect('/')
        else:
                form = RequestFormAssign(instance=toassign)
        return render(request, 'Calendar/assign.html', {'form' : form})

#classe servant d'intermediaire pour la construction de la vue calendrier
class envTmp:
	def __init__(self, name):
		self.name = name
		self.reqlist = []	

	def add_req(self, req):
		self.reqlist.append(req)

	def sortreq(self):
		self.reqlist = sorted(self.reqlist, key=lambda req: req[0].end)

	def assignzoffset(self):
		for i, r in enumerate(self.reqlist):
			if i < len(self.reqlist) - 1:
				if r[0].end > self.reqlist[i+1][0].start:
					for p in range(i+1, len(self.reqlist)):
						self.reqlist[p][1].yoffset += 33
			
			

class reqProps:
	def __init__(self, req, indice, start_date, end_date):
		if req.start < start_date.date() and req.end < end_date.date():
			print "premier"
			self.offset = 0
			self.size = (req.end - start_date.date()).days*indice
			#print self.title, self.size
		elif req.start >= start_date.date() and req.end > end_date.date():
			print "secomd"
			self.size = (end_date.date() + datetime.timedelta(days=1) - req.start).days*indice
			self.offset = indice*(req.start - start_date.date()).days
		elif req.start < start_date.date() and req.end >= end_date.date():
			print "^derniesiemeo"
			self.size = (end_date + datetime.timedelta(days=1) - start_date).days*indice
			#print (end_date - start_date).days, indice
			#print "############################", self.size
			self.offset = 0 
		else:
			print "dernier"
			self.size = (req.end + datetime.timedelta(days=1)- req.start).days*indice
			#print self.title, self.size
			self.offset = indice*(req.start - start_date.date()).days
		self.yoffset = 0

	


def makeView(request):
	form = InputDateForm()
	if request.method=='GET':
		form = InputDateForm(request.GET)
		if form.is_valid():
			 #recuperation des dates de debut et de fin
                        datefrom = datetime.datetime.strptime(request.GET['datefrom'], '%m/%d/%Y')
                        dateto = datetime.datetime.strptime(request.GET['dateto'], '%m/%d/%Y')

			##### to finish ######
                        infostech = []
                        nbjours = (dateto + datetime.timedelta(days=1)- datefrom).days if (dateto - datefrom).days > 0 else 1
                        infostech.append(nbjours)
                        indice = 1000/nbjours
                        infostech.append(indice)
                        etiquettewidth = 50
                        infostech.append(etiquettewidth)
                        datelist = []
			mounthlist = [] 
			monthinit = datefrom.strftime("%B")
			msize = 0
			offset = 76
                        for date_un in range(nbjours):
				mcurrent = (datefrom + datetime.timedelta(days=date_un)).strftime("%B")
				if mcurrent == monthinit:
					msize += 1
				else:
					mounthlist.append((monthinit, msize, offset))
					monthinit = mcurrent
					offset += msize*indice
					msize = 1
                                datelist.append(datefrom + datetime.timedelta(days=date_un))
			mounthlist.append((monthinit, msize, offset))
			#recuperation de la liste des environnements existants dans la db
			existingEnvs = Envs.objects.all()[:]
			#construction de la liste des requetes correspondant aux dates
			reqsIN = Request.objects.filter(start__gte=datefrom).filter(end__lte=dateto)
			reqsL = Request.objects.filter(start__lt=datefrom).filter(end__gt=datefrom).filter(end__lte=dateto)
			reqsR = Request.objects.filter(start__lt=dateto).filter(end__gt=dateto).filter(start__gte=datefrom)
			reqsA = Request.objects.filter(start__lt=datefrom).filter(end__gt=dateto)
			#discrimination des requetes par environnement
			finalList = []
			for en in existingEnvs:
				e = envTmp(en.name)
				for req in reqsIN:
					if req.env:
						if req.env.name == e.name:
							#if e.name == "ENV1":
							#	print "1env4"
							props = reqProps(req, indice, datefrom, dateto)
							print "premier", req.get_apps()
							e.add_req((req, props))
				for ree in reqsL:
					if ree.env:
						if ree.env.name == e.name:
							#if e.name == "ENV1":
							#	print "2env4"
							props = reqProps(ree, indice, datefrom, dateto)
							print "second", ree.get_apps()
							e.add_req((ree, props))
				for reqq in reqsR:
        	                         if reqq.env:
	                                 	if reqq.env.name == e.name:
							#if e.name == "ENV1":
							#	print "3env4"
							props = reqProps(reqq, indice, datefrom, dateto)
							print "Avant dernier", reqq.get_apps()
                        	                        e.add_req((reqq, props))
                                for reqqs in reqsA:
                               		if reqqs.env:
                                        	if reqqs.env.name == e.name:
							#if e.name == "ENV1":
							#	print "4env4"
                                                        props = reqProps(reqqs, indice, datefrom, dateto)
							print "Last", reqqs.get_apps()
                                                        e.add_req((reqqs, props))

				e.sortreq()
				e.assignzoffset()
				finalList.append(e)

			print len(finalList)
			return render(request, 'Calendar/view.html', {'reqs' : finalList, 'form' : form, 'infos' : infostech, 'dates' : datelist, 'month': mounthlist })
		else:
			return render(request, 'Calendar/view.html', {'form' : form})

class InputDateForm(forms.Form):

	def __init__(self, *args, **kwargs):
		super(InputDateForm, self).__init__(*args, **kwargs)
		self.fields['datefrom'].required = False
		self.fields['dateto'].required = False
	
	datefrom = forms.DateField(('%m/%d/%Y',), label='Debut', initial=datetime.date.today, widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'datefromselect'}))
	dateto = forms.DateField(('%m/%d/%Y',), label='Fin', initial=datetime.datetime.now() + datetime.timedelta(days=30), widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'datetoselect'}))

	def clean_datefrom(self):
		if not self.cleaned_data.get('datefrom'):
			self.fields['datefrom'].value = datetime.date.today
		return self.cleaned_data.get('datefrom') 

	def clean_dateto(self):
		cleaned_data = self.cleaned_data	
		ffrom = cleaned_data.get('datefrom')
		tto = cleaned_data.get('dateto')
		if tto < ffrom:
			raise forms.ValidationError("La date de debut doit etre inferieure a la date de fin")
		if not tto:
			self.fields['dateto'].value = datetime.datetime.now() + datetime.timedelta(days=30)
		return cleaned_data


@login_required
def login(request):
	return HttpResponseRedirect('/')	

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')
