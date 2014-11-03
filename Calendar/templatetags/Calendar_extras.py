from django import template
from datetime import datetime
import time
from datetime import date

register = template.Library()

@register.filter
def multiply(value, arg):
    return value*arg


@register.filter
def range(value):
	return xrange(value)


@register.filter
def displaydaydate(value):
	return date.strftime(value, '%d') 


@register.filter
def dateop(value, arg):
	return (value - arg).days

@register.filter
def appslist(obj):
	return obj.get_apps()

@register.filter
def findin(value, string):
	if value.find(string) != -1:
		return True
	else:
		return False

@register.filter
def capitalize(value):
	return value.title()
