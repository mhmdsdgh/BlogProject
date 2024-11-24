import json
from django import template
from ..models import Post, Comment
from django.db.models import Count
from markdown import markdown
from django.utils.safestring import mark_safe
from persiantools import digits
from collections import Counter
from django.urls import reverse

# from translate import Translator

register = template.Library()


@register.simple_tag(name="tp")
def total_posts():
    return Post.published.count()


@register.simple_tag(name="tc")
def total_comments():
    return Comment.objects.filter(active=True).count()


@register.simple_tag(name="lpd")
def last_post_date():
    try:
        return Post.published.last().publish
    except:
        pass


# @register.simple_tag
# def most_popular_posts(count=8):
#     return Post.published.annotate(comments_count=Count('comments')).order_by('-comments_count')[:count]


@register.inclusion_tag("partials/latest_posts.html")
def latest_posts(count=8):
    l_posts = Post.published.order_by('-publish')[:count]
    context = {
        "l_posts": l_posts
    }
    return context


@register.inclusion_tag("partials/pop_posts.html")
def most_popular_posts(count=8):
    pop_posts = Post.published.annotate(comments_count=Count('comments')).order_by('-comments_count')[:count]
    context = {
        "pop_posts": pop_posts
    }
    return context


@register.filter(name='markdown')
def to_markdown(text):
    return mark_safe(markdown(text))


# @register.simple_tag(name="check")
# def check_user_id(user_id):
#     try:
#         _ = ControlUsers.objects.get(user_id=user_id)

#     except:
#         pass

#     finally:
#         return True

@register.filter()
def censor(value):
    s2 = '...'
    censor_list = ["کیر", "سیک", "کص", "جنده", "قحبه", "fuck", "Fuck", "FUCK", "milf", "دیوث", "جاکش"]
    for i in censor_list:
        s3 = value.replace(f'{i}', s2)
        value = s3
    return value


@register.simple_tag(name='p_img_src')
def post_image_src(post):
    try:
        py_type = json.loads(post.PATH_LIST.replace("\'", "\""))
        return py_type['1']
    except json.JSONDecodeError:
        pass


@register.simple_tag(name='date_converter')
def date_converter(date):
    persian_num = digits.en_to_fa(f"{date}")
    # translator = Translator(to_lang='fa')
    # return translator.translate(persian_num)
    return persian_num


@register.inclusion_tag('partials/navigation.html', name='popular_tags')
def popular_tags(category):
    posts = Post.published.filter(category=str(category))
    tags = []
    for post in posts:
        post_tags = post.tags.all()
        for post_tag in post_tags.values():
            tags.append(post_tag['name'])
        # tags.append(post_tags[:5])

    if len(tags) == 0:
        return None

    total_tags = []
    # for _ in tags:
    # the_tag = max(set(tags), key=tags.count)
    the_tags = Counter(tags).most_common(5)
    # print(the_tags)

    for tag in the_tags:
        total_tags.append(tag[0])

    # the_tags.append(the_tag[0])
    # tags.remove(the_tag)

    context = {
        'the_tags': total_tags
    }

    return context


@register.simple_tag()
def link_maker(category):
    return reverse('blog:post_list_category', args=[category])

# @register.inclusion_tag('partials/pagination.html')
# def pagination(count=8):
#     pass


@register.simple_tag()
def posts_counter(user):
    posts_count = Post.published.filter(author=user).count()
    # print(posts_count)
    return date_converter(posts_count)


@register.simple_tag()
def persian_categories(category):
    if category == 'philosophical':
        return 'فلسفی'

    if category == 'popular-philosophers':
        return 'فلاسفه معروف'

    if category == 'books':
        return 'کتاب ها'

    if category == 'psychology':
        return 'روانشناسی و سبک زندگی'
    else:
        return 'سیاست و تاریخ'


@register.filter()
def tag_slug(tag):
    tag_name = tag[1].replace(' ', '-')
    return tag_name


@register.filter()
def footer_slug(tag):
    tag_name = tag.replace(' ', '-')
    return tag_name


@register.inclusion_tag('partials/footer.html')
def footer_tags():
    posts = Post.published.all()
    tags = []
    for post in posts:
        post_tags = post.tags.all()
        for post_tag in post_tags.values():
            tags.append(post_tag['name'])
        # tags.append(post_tags[:5])

    if len(tags) == 0:
        return None

    total_tags = []
    # for _ in tags:
    # the_tag = max(set(tags), key=tags.count)
    the_tags = Counter(tags).most_common(12)
    # print(the_tags)

    for tag in the_tags:
        total_tags.append(tag[0])

    # the_tags.append(the_tag[0])
    # tags.remove(the_tag)

    context = {
        'footer_tags': total_tags
    }

    return context

