from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from myblog.models import Post
from myblog.forms import PostForm, UserForm
from django.utils import timezone

posts = None
previousRequest = None

def index(request):
	global posts
	global previousRequest
	if request.user.is_active:
		posts = Post.objects.all().order_by('-published_date')
	else:
		posts = None
	if previousRequest == "editpost":
		context_dict = {'posts': posts, 'prompt': True}
	else:
		context_dict = {'posts': posts, 'prompt': False}
	previousRequest = "index"
	return render(request, 'myblog/index.html', context_dict)

def register(request):
	global previousRequest
	previousRequest = "register"
	if request.method == 'POST':
		user_form = UserForm(request.POST)
		username = request.POST.get('username')
		password = request.POST.get('password')
		print("Username is " + username)
		print("Password is " + password)
		if user_form.is_valid():
			user = user_form.save(commit = True)
			print("Username is " + user.username)
			print("Password is " + user.password)
			user.set_password(user.password)
			user.save()
			return HttpResponseRedirect(reverse('myblog:login'))
	else:
		user_form = UserForm()
	context_dict = {'user_form': user_form}
	return render(request, 'myblog/register.html', context_dict)


def user_login(request):
	global previousRequest
	previousRequest = "user_login"
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username = username, password = password)
		if user:
			if user.is_active:
				print("Username is " + username)
				print("Password is " + password)
				login(request, user)
				global prompt
				prompt = False
				return HttpResponseRedirect(reverse('myblog:index'))
			else:
				return HttpResponse("Your account is disabled")
		else:
			return HttpResponse("Please enter valid credentials")
	else:
		return render(request, 'myblog/login.html', {})
		
def user_logout(request):
	global previousRequest
	previousRequest = "user_logout"
	logout(request)
	global posts
	posts = None
	prompt = False
	return HttpResponseRedirect(reverse('myblog:index'))

def addpost(request):
	global previousRequest
	previousRequest = "addpost"
	if request.method == 'POST':
		post_form = PostForm(request.POST)
		if post_form.is_valid():
			post = post_form.save(commit = False)
			post.published_date = timezone.now();
			post.author = request.user
			post.save()
			return HttpResponseRedirect(reverse('myblog:index'))
		else:
			context_dict = {'post_form': post_form}
			return render(request, 'myblog/addpost.html', context_dict)
	else:
		post_form = PostForm()
		context_dict = {'post_form': post_form}
		return render(request, 'myblog/addpost.html', context_dict)

def editpost(request, pk):
	post = get_object_or_404(Post, pk = pk)
	global previousRequest
	if post.author != request.user:
		previousRequest = "editpost"
		return HttpResponseRedirect(reverse('myblog:index'))
	if request.method == 'POST':
		post_form = PostForm(request.POST, instance = post)
		if post_form.is_valid():
			post = post_form.save(commit = False)
			post.published_date = timezone.now();
			post.author = request.user
			post.save()
			return HttpResponseRedirect(reverse('myblog:index'))
		else:
			context_dict = {'post_form': post_form}
			return render(request, 'myblog/editpost.html', context_dict)
	else:
		post_form = PostForm(instance = post)
		context_dict = {'post_form': post_form, 'pk': pk}
		return render(request, 'myblog/editpost.html', context_dict)

