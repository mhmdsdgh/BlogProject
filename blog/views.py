# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
# from django.http import HttpResponse, Http404
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
# from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from taggit.models import Tag

# Create your views here.


def index(request, count=8):
    posts = Post.published.annotate(likes_count=Count('likes')).order_by('-likes_count')[:count]
    top_authors = User.objects.annotate(posts_count=Count('posts')).order_by('-posts_count')[:5]

    context = {
        'posts': posts,
        'top_authors': top_authors,
    }

    return render(request, "blog/index.html", context)

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = "posts"
#     paginate_by = 3
#     template_name = "blog/list.html"


def post_list(request, category=None, tag_slug=None):
    # post = Post.objects.filter(status="The post")
    tag = None
    if category is not None:
        posts = Post.published.filter(category=category)
    elif tag_slug is not None:
        tag = get_object_or_404(Tag, slug=tag_slug)
        # many-to-many relationship
        posts = Post.published.filter(tags__in=[tag])
    else:
        posts = Post.published.all()
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page', 1)

    if posts.count() > 10:
        try:
            posts = paginator.page(page_num)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

    context = {
        'posts': posts,
        'category': category,
        'tag': tag,
    }
    return render(request, "blog/recent_posts.html", context)


def post_detail(request, pk, slug):

    post = get_object_or_404(Post, id=pk, slug=slug, status=Post.Status.PUBLISHED)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:4]
    comments = post.comments.filter(active=True) 
    form = CommentForm()

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            form = PostForm

    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'similar_posts': similar_posts,
    }

    return render(request, "blog/detail.html", context)
    
# class PostDetailView(DetailView):
#     form = CommnetForm()
#     comments = Post.comments.filter(active=True)
#     model = {
#         'post': Post,
#         'form': form,
#         'comments': comments,
#     }
#     template_name = "blog/detail.html"


def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            Ticket.objects.create(message=cd['message'], name=cd['name'], email=cd['email'],
                                  phone=cd['phone'], subject=cd['subject'])
            return redirect("blog:index")
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    # comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    # context = {
    #     'post': post,
    #     'form': form,
    #     "comment": comment
    # }
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('blog:profile')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect(reverse('blog:index'))
    else:
        form = PostForm()
    return render(request, 'forms/create_post.html', {'form': form})


# def post_search(request):
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(data=request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             search_query = SearchQuery(query) | SearchQuery('جنگو')
#             search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='A')\
#                         + SearchVector('slug', weight='D')
#             results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).\
#                 filter(rank__gte=0.5).order_by('-rank')
#     context = {
#         'query': query,
#         'results': results
#     }
#     return render(request, 'blog/search.html', context)

# def post_search(request):
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(data=request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             results1 = Post.published.annotate(similarity=TrigramSimilarity('title', query))\
#                 .filter(similarity__gt=0.1).order_by('-similarity')
#             results2 = Post.published.annotate(similarity=TrigramSimilarity('description', query))\
#                 .filter(similarity__gt=0.1).order_by('-similarity')
#             results = (results1 | results2 ).order_by('-similarity')
#     context = {
#         'query': query,
#         'results': results
#     }
#     return render(request, 'blog/search.html', context)


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results1 = Post.published.annotate(similarity=TrigramSimilarity('title', query))\
                .filter(similarity__gt=0.1)
            results2 = Post.published.annotate(similarity=TrigramSimilarity('content', query))\
                .filter(similarity__gt=0.2)
            results = (results1 | results2).order_by('-similarity')
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'blog/search.html', context)


@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    posts = Post.published.filter(author=user)
    paginator = Paginator(posts, 6)
    page_num = request.GET.get('page', 1)
    following_users = user.following.all()
    following_posts = []

    for f_user in following_users:
        for post in f_user.posts.filter(status=Post.Status.PUBLISHED)[:8]:
            following_posts.append(post)

    if posts.count() > 6:
        try:
            posts = paginator.page(page_num)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

    context = {
        'posts': posts,
        'user': user,
        'following_posts': following_posts,
        'following_users': following_users,

    }

    return render(request, 'blog/my_profile.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect('blog:profile')
    return render(request, 'forms/delete-post.html', {'post': post})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('blog:index'))
    else:
        form = PostForm(instance=post)
    return render(request, 'forms/create_post.html', {'form': form})


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id:
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        # unlike:
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        post_likes_count = post.likes.count()

        response_data = {
            'liked': liked,
            'likes_count': post_likes_count,
        }

    else:
        response_data = {
            'error': 'Invalid post_id'
        }

    return JsonResponse(response_data)


@require_POST
@login_required
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id:
        post = Post.objects.get(id=post_id)
        user = request.user

        # unlike:
        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True

        return JsonResponse({'saved': saved})

    return JsonResponse({'error': 'invalid request'})

# def user_login(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, username=cd['username'], password=cd['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return HttpResponse('You are logged in!')
#                 else:
#                     return HttpResponse('Your account is disabled.')
#             else:
#                 return HttpResponse('Your are not logged in!')
#     else:
#         form = LoginForm()
#     return render(request, 'forms/login.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('blog:index')
    # return redirect(request.META.get('HTTP_REFERER'))


@login_required
def edit_user(request):
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user, files=request.FILES)
        if user_form.is_valid():
            user_form.save()
            return redirect('blog:profile')
    else:
        user_form = EditUserForm(instance=request.user)
    context = {
        'user_form': user_form
    }
    return render(request, 'registration/edit_account.html', context)


# Other users profiles view #
def user_profile(request, user_name):
    user = get_object_or_404(User, username=user_name)
    if request.user == user:
        return redirect('blog:profile')
    posts = Post.published.filter(author=user)
    posts_count = posts.count()
    paginator = Paginator(posts, 6)
    page_num = request.GET.get('page', 1)

    if posts.count() > 6:
        try:
            posts = paginator.page(page_num)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

    context = {
        'user': user,
        'posts': posts,
        'posts_count': posts_count
    }

    return render(request, 'blog/user_profile.html', context)


@login_required
def show_comments(request):
    posts = Post.published.filter(author=request.user)

    if posts.count() > 20:
        paginator = Paginator(posts, 20)
        page_num = request.GET.get('page', 1)

        try:
            posts = paginator.page(page_num)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

    context = {
        'posts': posts,
    }

    return render(request, 'blog/show_comments.html', context)


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                follow = True
            following_count = user.following.count()
            followers_count = user.followers.count()
            return JsonResponse({'follow': follow, 'followers_count': followers_count,
                                 'following_count': following_count})

        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'})
    return JsonResponse({'error': 'Invalid request'})


@login_required
def saved_posts(request):
    user = User.objects.get(id=request.user.id)
    posts = user.saved_posts.all()

    paginator = Paginator(posts, 6)
    page_num = request.GET.get('page', 1)

    s_posts = True

    if posts.count() > 6:
        try:
            posts = paginator.page(page_num)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            posts = paginator.page(1)

    context = {
        'user': user,
        'posts': posts,
        's_posts': s_posts,
    }

    return render(request, 'blog/recent_posts.html', context)
