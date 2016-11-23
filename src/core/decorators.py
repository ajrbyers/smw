from django.core import exceptions
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.core.urlresolvers import reverse
from core import models
from submission import models as submission_models

from pprint import pprint
from itertools import chain

def is_author(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		if 'author' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Author level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def is_press_editor(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]

		if 'press-editor' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap	

def is_production_editor(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]

		if 'production-editor' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Production Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap	


def is_editor(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		if 'press-editor' in user_roles or 'series-editor' in user_roles or 'book-editor' in user_roles or 'production-editor' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def is_book_editor(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		# Check if the user is a press-editor, if not, check if they are they are assigend as an editor to this book, or check if the user is the series editor for this book.
		if 'press-editor' in user_roles:
			return function(request, *args, **kwargs)
		elif submission_id:
			book = get_object_or_404(models.Book, pk=submission_id)
			if request.user in book.book_editors.all() or book.series in request.user.series_set.all():
				return function(request, *args, **kwargs)
			else:
				messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
				raise exceptions.PermissionDenied 
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def is_book_editor_or_author(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		# Check if the user is a press-editor, if not, check if they are they are assigend as an editor to this book, or check if the user is the series editor for this book.
		if 'press-editor' in user_roles:
			return function(request, *args, **kwargs)
		elif submission_id:
			book = get_object_or_404(models.Book, pk=submission_id)
			if request.user in book.book_editors.all() or book.series in request.user.series_set.all() or book.owner == request.user:
				return function(request, *args, **kwargs)
			else:
				messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
				raise exceptions.PermissionDenied 
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def is_reviewer(function):
	def wrap(request, *args, **kwargs):
		one_click_no_login = models.Setting.objects.filter(name='one_click_review_url')
		if one_click_no_login:
			if one_click_no_login[0].value == 'on':
				full_url = request.get_full_path()
				if 'access_key' in full_url:
					if 'decision' in full_url:
						access_key = full_url[full_url.rfind('key/')+4:]
						access_key = access_key.split('/', 1)[0]
					elif 'complete' in full_url:
						access_key = full_url[full_url.rfind('key/')+4:]
						access_key = access_key.split('/', 1)[0]
					else:
						access_key = full_url[full_url.rfind('key/')+4:]
						access_key = access_key[:access_key.rfind('/')]
					review_assignments = models.ReviewAssignment.objects.filter(access_key=access_key)
					proposal_review_assignments = submission_models.ProposalReview.objects.filter(access_key=access_key)
					if review_assignments or proposal_review_assignments:
						return function(request, *args, **kwargs)


		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		# Check if the user is a press-editor, if not, check if they are they are assigned as an editor to this book, or check if the user is the series editor for this book.
		if 'press-editor' in user_roles:
			return function(request, *args, **kwargs)
		elif submission_id:
			book = get_object_or_404(models.Book, pk=submission_id)
			if request.user in [reviewer.user for reviewer in book.reviewassignment_set.all()] or book.owner == request.user:
				return function(request, *args, **kwargs)
			else:
				messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
				raise exceptions.PermissionDenied 
		elif not submission_id and 'reviewer' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def has_reviewer_role(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		if 'reviewer' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Reviewer level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def is_indexer(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		# Check if the user is a press-editor, if not, check if they are they are assigend as an editor to this book, or check if the user is the series editor for this book.
		if 'press-editor' in user_roles:
			return function(request, *args, **kwargs)
		elif submission_id:
			book = get_object_or_404(models.Book, pk=submission_id)
			if request.user in [reviewer.indexer for reviewer in book.indexassignment_set.all()] or book.owner == request.user:
				return function(request, *args, **kwargs)
			else:
				messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
				raise exceptions.PermissionDenied
		elif not submission_id and 'indexer' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap


def is_copyeditor(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		# Check if the user is a press-editor, if not, check if they are they are assigend as an editor to this book, or check if the user is the series editor for this book.
		if 'press-editor' in user_roles:
			return function(request, *args, **kwargs)
		elif submission_id:
			book = get_object_or_404(models.Book, pk=submission_id)
			if request.user in [reviewer.copyeditor for reviewer in book.copyeditassignment_set.all()] or book.owner == request.user:
				return function(request, *args, **kwargs)
			else:
				messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
				raise exceptions.PermissionDenied 
		elif not submission_id and 'copyeditor' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def is_typesetter(function):
	def wrap(request, *args, **kwargs):
		
		if not request.user.is_authenticated():
			messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
			return redirect("%s?next=%s" % (reverse('login'), request.get_full_path()))

		user_roles = [role.slug for role in request.user.profile.roles.all()]
		submission_id = False
		
		if kwargs.get('submission_id'):
			submission_id = kwargs.get('submission_id')

		# Check if the user is a press-editor, if not, check if they are they are assigned as an editor to this book, or check if the user is the series editor for this book.
		if 'press-editor' in user_roles:
			return function(request, *args, **kwargs)
		elif submission_id:
			book = get_object_or_404(models.Book, pk=submission_id)
			if request.user in [reviewer.typesetter for reviewer in book.copyeditassignment_set.all()] or book.owner == request.user:
				return function(request, *args, **kwargs)
			else:
				messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
				raise exceptions.PermissionDenied
		elif not submission_id and 'typesetter' in user_roles:
			return function(request, *args, **kwargs)
		else:
			messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
			raise exceptions.PermissionDenied 

	wrap.__doc__=function.__doc__
	wrap.__name__=function.__name__
	return wrap

def is_onetasker(function):
		def wrap(request, *args, **kwargs):

			if not request.user.is_authenticated():
				messages.add_message(request, messages.ERROR, 'You need to log in to view this page.')
				raise exceptions.PermissionDenied 

			user_roles = [role.slug for role in request.user.profile.roles.all()]
			submission_id = False
			
			if kwargs.get('submission_id'):
				submission_id = kwargs.get('submission_id')

			# Check if the user is a press-editor, if not, check if they are they are assigned as an editor to this book, or check if the user is the series editor for this book.
			if 'press-editor' in user_roles:
				return function(request, *args, **kwargs)
			elif submission_id:
				book = get_object_or_404(models.Book, pk=submission_id)
				if request.user in book.onetaskers() or request.user in book.all_editors() or book.owner == request.user:
					return function(request, *args, **kwargs)
				else:
					messages.add_message(request, messages.ERROR, 'You do not have permission to access this resource.')
					raise exceptions.PermissionDenied 
			elif not submission_id and (set(user_roles) & set(['copyeditor', 'typesetter', 'indexer'])):
				return function(request, *args, **kwargs)
			else:
				messages.add_message(request, messages.ERROR, 'You need to have Press Editor, Book Editor or Series Editor level permission to view this page.')
				raise exceptions.PermissionDenied 

		wrap.__doc__=function.__doc__
		wrap.__name__=function.__name__
		return wrap









