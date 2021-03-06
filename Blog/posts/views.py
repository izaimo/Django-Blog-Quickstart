from urllib import quote_plus
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import PostForm
from .models import Post
from django.db.models import Q

from django.shortcuts import render


# Create your views here.
def post_create(request): #create post
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        print form.cleaned_data.get("title")
        instance.save()
        messages.success(request,"Article Posted Successfully!", extra_tags="glyphicon glyphicon-ok")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form,
    }
    return render(request,"form.html", context)


def post_detail(request, slug=None):
        instance = get_object_or_404(Post, slug=slug)
        if instance.publish > timezone.now().date() or instance.draft:
            if not request.user.is_staff or not request.user.is_superuser:
                raise Http404
        context = {
            "title": instance.title,
            "instance": instance,
        }
        return render(request, "single_post.html", context)


def post_list(request): #list posts
    today = timezone.now().date()
    queryset_list = Post.objects.active().order_by("-created")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()

    #search posts
    search = request.GET.get("search")
    if search:
        queryset_list = queryset_list.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        ).distinct()

    #pagination
    paginator = Paginator(queryset_list, 5) #Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context ={
        "object_list": queryset,
        "title": "My Posts",
        "page_request_var": page_request_var,
        "today": today,
    }

    return render(request,"posts.html", context)


def post_update(request, slug=None): #update post
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post,slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request,"Article Edited Successfully!", extra_tags="glyphicon glyphicon-ok")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form":form,
    }
    return render(request,"form.html", context)


def post_delete(request, slug=None): #delete post
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request,"Article Deleted Successfully!", extra_tags="glyphicon glyphicon-ok")
    return redirect("posts:list")