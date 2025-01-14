from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.db.models import Q
from django.views import View
from django.contrib.auth.models import User

from .models import BlogModel, ProfileOfUser, Follow


class LoginView(auth_views.LoginView):
    template_name = 'core/form.html'    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        context['form_title'] = 'Login'
        context['form_btn'] = 'Login'
        return context
    

class RegisterView(View):
    template_name = 'core/form.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            ProfileOfUser.objects.create(user=user)
            login(request, user)
            return redirect('home')
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})


class HomePageView(ListView):
    model = BlogModel
    template_name = 'core/index.html'
    context_object_name = 'blogs'
    paginate_by = 5

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        queryset = BlogModel.objects.all()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query)
            )

        queryset = queryset.order_by('-created_at')

        return queryset


class ProfilePageView(ListView):
    model = BlogModel
    template_name = 'core/my_blogs_profile.html'
    context_object_name = 'blogs'
    ordering = ['-created_at']
    paginate_by = 10

    def get_user(self):
        user_id = self.kwargs.get('user_id')
        
        if user_id:
            return User.objects.get(pk=user_id)
        else:
            return self.request.user
            # return self.request.user

    def get_queryset(self):
        user = self.get_user()
        return BlogModel.objects.filter(author=user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_user()
        context['profile'] = ProfileOfUser.objects.filter(user=user).first()
        context['followers'] = Follow.objects.filter(following=user)
        context['following'] = Follow.objects.filter(follower=user)
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.filter(
                    follower=self.request.user,
                    following=user
            ).exists()
        return context


    
class ChangeProfile(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ProfileOfUser
    template_name = 'core/form.html'
    fields = ['bio', 'picture']
    success_message = 'The profile info was successfully updated.'

    def get_object(self, queryset=None):
        return ProfileOfUser.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Profile'
        context['form_title'] = 'Update Profile'
        context['form_btn'] = 'Update'
        context['with_media'] = True
        return context


class BlogDetailView(DetailView):
    model = BlogModel
    template_name = 'core/blog_detail.html'
    context_object_name = 'blog'

    def get(self, request, *args, **kwargs):
        # Get the blog object
        blog = self.get_object()

        blog.save()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_object().title
        return context


class BlogCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BlogModel
    template_name = 'core/form.html'
    fields = ['title', 'content', 'media']
    success_message = 'The blog post was successfully posted.'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Make Blog'
        context['form_title'] = 'Make Blog'
        context['form_btn'] = 'Post'
        context['with_media'] = True
        return context
    
class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = BlogModel
    template_name = 'core/form.html'
    fields = ['title', 'content', 'media']
    success_message = 'The blog post was successfully updated.'

    def test_func(self):
        # Check if the authenticated user is the author of the blog
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Blog'
        context['form_title'] = 'Update Blog'
        context['form_btn'] = 'Update'
        context['with_media'] = True
        return context


class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = BlogModel
    template_name = 'core/blog_delete.html'
    success_url = reverse_lazy('home')  # Redirect to the home page after deletion
    context_object_name = 'blog'
    success_message = 'The blog post was successfully deleted.'
    
    def test_func(self):
        # Check if the authenticated user is the author of the blog
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Blog'
        return context
    

# class showFollow():
