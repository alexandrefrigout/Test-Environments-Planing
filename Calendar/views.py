from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth.decorators import login_required
import time
from datetime import date
from datetime import datetime
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
		self.reqlist = sorted(self.reqlist, key=lambda req: req.end)

	def assignzoffset(self):
		for i, r in enumerate(self.reqlist):
			if i < len(self.reqlist) - 1:
				if r.end > self.reqlist[i+1].start:
					for p in range(i+1, len(self.reqlist)):
						self.reqlist[p].yoffset += 33
			
			

class reqTmp:
	def __init__(self, req, indice, start_date, end_date):
		self.__dict__ = req.__dict__
		if req.start < start_date.date() and req.end < end_date.date():
			#print "premier"
			self.offset = 0
			self.size = (req.end - start_date.date()).days*indice
			print self.title, self.size
		elif req.start > start_date.date() and req.end > end_date.date():
			#print "secomd"
			self.size = (end_date.date() - req.start).days*indice
			self.offset = indice*(req.start - start_date.date()).days
			print "11111", self.title, self.size
		elif req.start < start_date.date() and req.end > end_date.date():
			#print "^derniesiemeo"
			self.size = (end_date - start_date).days*indice
			print (end_date - start_date).days, indice
			print "############################", self.size
			self.offset = 0 
		else:
			#print "dernier"
			self.size = (req.end - req.start).days*indice
			print self.title, self.size
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
                        nbjours = (dateto - datefrom).days if (dateto - datefrom).days > 0 else 1
                        infostech.append(nbjours)
                        indice = int(1000/nbjours)
                        infostech.append(indice)
                        etiquettewidth = 50
                        infostech.append(etiquettewidth)
                        datelist = []
                        for date_un in range(nbjours):
                                datelist.append(datefrom + datetime.timedelta(days=date_un))
			#recuperation de la liste des environnements existants dans la db
			existingEnvs = Envs.objects.all()[:]
			#construction de la liste des requetes correspondant aux dates
			reqsIN = Request.objects.filter(start__gte=datefrom).filter(end__lte=dateto)
			reqsL = Request.objects.filter(start__lt=datefrom).filter(end__gt=datefrom).filter(end__lt=dateto)
			reqsR = Request.objects.filter(start__lt=dateto).filter(end__gt=dateto).filter(start__gt=datefrom)
			reqsA = Request.objects.filter(start__lt=datefrom).filter(end__gt=dateto)
			print len(reqsIN), len(reqsL), len(reqsR), len(reqsA)
			#discrimination des requetes par environnement
			finalList = []
			for en in existingEnvs:
				e = envTmp(en.name)
				for req in reqsIN:
					if req.env:
						if req.env.name == e.name:
							if e.name == "ENV4":
								print "1env4"
							tmpreq = reqTmp(req, indice, datefrom, dateto)
							e.add_req(tmpreq)
				for re in reqsL:
					if re.env:
						if re.env.name == e.name:
							if e.name == "ENV4":
								print "2env4"
							tmpreq = reqTmp(re, indice, datefrom, dateto)
							e.add_req(tmpreq)
				for reqq in reqsR:
        	                         if reqq.env:
	                                 	if reqq.env.name == e.name:
							if e.name == "ENV4":
								print "3env4"
                	                        	tmpreq = reqTmp(reqq, indice, datefrom, dateto)
                        	                        e.add_req(tmpreq)
                                for reqqs in reqsA:
                               		if reqqs.env:
                                        	if reqqs.env.name == e.name:
							if e.name == "ENV4":
								print "4env4"
                                                	tmpreq = reqTmp(reqqs, indice, datefrom, dateto)
                                                        e.add_req(tmpreq)

				e.sortreq()
				e.assignzoffset()
				finalList.append(e)
				print en.name, len(e.reqlist)

			print len(finalList)
			return render(request, 'Calendar/view.html', {'reqs' : finalList, 'form' : form, 'infos' : infostech, 'dates' : datelist})
		else:
			return render(request, 'Calendar/view.html', {'form' : form})

class InputDateForm(forms.Form):

	#def __init__(self, *args, **kwargs):
	#	super(InputDateForm, self).__init__(*args, **kwargs)
	#	self.fields['datefrom'].required = False
	#	self.fields['dateto'].required = False
	
	datefrom = forms.DateField(('%m/%d/%Y',), label='Debut', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'datefromselect'}))
	dateto = forms.DateField(('%m/%d/%Y',), label='Fin', widget=forms.DateTimeInput(format='%m/%d/%Y', attrs={'id':'datetoselect'}))

	def clean_dateto(self):
		cleaned_data = self.cleaned_data	
		ffrom = cleaned_data.get('datefrom')
		tto = cleaned_data.get('dateto')
		if tto < ffrom:
			raise forms.ValidationError("La date de debut doit etre inferieure a la date de fin")
