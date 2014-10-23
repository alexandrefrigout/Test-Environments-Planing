from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth.decorators import login_required
import datetime
from Calendar.models import Envs, Application, Request



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
		exclude = ['env']


def create(request):
	if request.method == 'POST':
		form = RequestForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/')
		else:
			print form.errors
	else:
		form = RequestForm()
	return render(request, 'Calendar/createreq.html', {'form' : form})


def editRequest(request, title):
	tomodif = Request.objects.get(id=title)
	if request.method == 'POST':
		form = RequestForm(request.POST, instance=tomodif)	
		if form.is_valid():
                        form.save()
                        return HttpResponseRedirect('/')
	else:
                form = RequestForm(instance=tomodif)
        return render(request, 'Calendar/edit.html', {'form' : form})

def deleteRequest(request, title):
	todel = Request.objects.get(id=title)
	todel.delete()
	return HttpResponseRedirect('/')

def index(request):
	all_req = Request.objects.order_by('-date_creation')[:]
	return render(request, 'Calendar/index.html', {'list_req' : all_req})

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

def makeView(request):
	if 'datefrom' and 'dateto' in request.GET:
		if request.GET['datefrom']:
			#recuperation de la liste des environnements existants dans la db
			existingEnvs = Envs.objects.all()[:]
			#recuperation des dates de debut et de fin
			datefrom = datetime.datetime.strptime(request.GET['datefrom'], '%Y-%m-%d')
			dateto = datetime.datetime.strptime(request.GET['dateto'], '%Y-%m-%d')
			#construction de la liste des requetes correspondant aux dates
			reqs = Request.objects.filter(start__gte=datefrom).filter(end__lte=dateto)
			#discrimination des requetes par environnement
			finalList = []
			for en in existingEnvs:
				e = envTmp(en.name)
				for req in reqs:
					if req.env:
						if req.env.name == e.name:
				#			print req.env.name, e.name
				#			print "found"
							e.add_req(req)
				finalList.append(e)

			#for f in finalList:
			#	print f.name, len(f.reqlist)
		else:
			datefrom=datetime.datetime.now()
			dateto=datetime.datetime.now()
			reqs = Request.objects.filter(start__gte=datefrom).filter(end__lte=dateto)
	for i in finalList:
		print i.name
	nbjours = (dateto - datefrom).days
	indice = round(1200/nbjours)
	etiquettewidth = 50
	return render(request, 'Calendar/view.html', {'reqs' : finalList})
