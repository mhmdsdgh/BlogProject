from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django_jalali.db import models as jmodels
from django.template.defaultfilters import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from django_resized import ResizedImageField
from taggit.managers import TaggableManager
from mptt.models import MPTTModel, TreeForeignKey

# Managers


class PublishedManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

# Create your models here.


class User(AbstractUser):

    SOCIAL_MEDIA_CHOICES = {

    }

    date_of_birth = jmodels.jDateTimeField(verbose_name='تاریخ تولد', blank=True, null=True)
    bio = models.TextField(verbose_name='بیو', null=True, blank=True, default='')
    photo = ResizedImageField(upload_to=f'profile_images/', size=[500, 500], quality=75, crop=['middle', 'center'],
                              null=True, blank=True)
    job = models.CharField(verbose_name='شغل', blank=True, null=True, max_length=30)
    following = models.ManyToManyField('self', through='Contact', related_name='followers', symmetrical=False)

    telegram = models.URLField(verbose_name='تلگرام', blank=True, null=True, max_length=100)
    instagram = models.URLField(verbose_name='اینستاگرام', blank=True, null=True, max_length=100)
    website = models.URLField(verbose_name='وبسایت', blank=True, null=True, max_length=100)

    # symitrical = رابطه متقارن طبق پیش فرض جنگو اگر کاربری کاربر دیگر را فالو کند، این فالو برای هر دو کاربر اتفاق می افتد و هر دو همدیگر را فالو میکنند با تنظیم کردن این پارامتر به فالس از این اتفاق جلوگیری میکنیم

    def get_absolute_url(self):
        return reverse('social:user_detail', args=[self.username])


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DT', 'Draft'
        PUBLISHED = 'PD', 'Published'
        REJECTED = 'RG', 'Rejected'

    CATEGORY_CHOICES = {
        ('popular-philosophers', 'فلاسفه معروف'),
        ('books', 'کتاب ها'),
        ('psychology', 'سبک زندگی و روانشناسی'),
        ('history', 'سیاست و تاریخ'),
        ('philosophical', 'فلسفی'),
    }
    # relations

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="نویسنده")

    # Data fields
    title = models.CharField(max_length=100, verbose_name="عنوان")
    content = RichTextUploadingField(default='', verbose_name="متن و محتوا")
    slug = models.SlugField(max_length=100, allow_unicode=True)
    # Date
    publish = jmodels.jDateTimeField(default=timezone.now(), verbose_name="تاریخ انتشار")
    created = jmodels.jDateTimeField(auto_now_add=True)
    updated = jmodels.jDateTimeField(auto_now=True)
    # Choice Fields
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    reading_time = models.PositiveIntegerField(verbose_name="زمان مطالعه")
    category = models.CharField(choices=CATEGORY_CHOICES, default='philosophical', max_length=22, verbose_name="دسته بندی")
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_posts')
    PATH_LIST = models.CharField(default='', blank=True, max_length=8000)

    tags = TaggableManager(verbose_name='تگ ها')

    # objects = models.Manager()
    objects = jmodels.jManager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id, self.slug])

    def delete(self, *args, **kwargs):
        try:
            import os
            import json
            py_type = json.loads(self.PATH_LIST.replace("\'", "\""))
            for image_path in py_type:
                os.remove(f'/BlogProject/{image_path}')
        except:
            pass
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if 'src=' in self.content:
            the_dict = {}
            content_splited = self.content.split()
            img = 1
            for i in content_splited:
                if 'src=' in i:
                    path = i[4:].replace('"', '')
                    the_dict[str(img)] = path
                    img += 1
            # print(the_dict)
            if self.PATH_LIST == '':
                self.PATH_LIST = str(the_dict)
            else:
                if self.PATH_LIST != str(the_dict):
                    import os
                    import json
                    py_type = json.loads(self.PATH_LIST.replace("\'", "\""))
                    # print(py_type)
                    for image_path in py_type.values():
                        if image_path not in the_dict.values():
                            os.remove(f'/BlogProject/{image_path}')
                self.PATH_LIST = str(the_dict)
        else:
            if self.PATH_LIST != '':
                import os
                import json
                py_type = json.loads(self.PATH_LIST.replace("\'", "\""))
                for image_path in py_type.values():
                    os.remove(f'/BlogProject/{image_path}')
                self.PATH_LIST = ''

        super().save(*args, **kwargs)

    # def title_to_url(self):
    #     return self.title.replace(' ', '-')


# class Image(models.Model):
#     post = models.OneToOneField()


class Ticket(models.Model):
    message = models.TextField()
    name = models.CharField(max_length=250)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    subject = models.CharField(max_length=250)

    def __str__(self):
        return self.subject


class Comment(MPTTModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=250, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    body = models.TextField(verbose_name='متن')
    created = jmodels.jDateTimeField(auto_now_add=True)
    updated = jmodels.jDateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    class MPPTMeta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"

    def __str__(self) -> str:
        return f"{self.name}: {self.post}"


# class Image(models.Model):

#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name="پست")
#     title = models.CharField(max_length=100, verbose_name="عنوان", null=True, blank=True)
#     description = models.TextField(verbose_name="توضیحات", null=True, blank=True)

#     t = datetime.datetime.now()
#     shamsi = jdatetime.date.fromgregorian(day=t.day, month=t.month ,year=t.year)
#     folder_path = f'{str(shamsi.year)}-{str(shamsi.month)}'

#     image_file = ResizedImageField(upload_to=f'post_images/{folder_path}',
#                                    size=[1920, 1080], quality=75)
#     created = jmodels.jjdatetimefield(auto_now_add=True)

#     class Meta:
#         ordering = ['created']
#         indexes = [
#             models.Index(fields=['created'])
#         ]


#     def save(self, *args, **kwargs):
#         try:
#             os.mkdir(f"/Django/Coding/media/post_images/{Image.folder_path}")
#         except FileExistsError:
#             pass
#         super().save(*args, **kwargs)

#     def __str__(self) -> str:
#         # return self.title is self.title else
#         if isinstance(self.title, NoneType):
#             img = Image.objects.filter(image_file=self.image_file)
#             name = img.values()[0]['image_file'][19:]
#             self.title = name
#         return self.title

# @receiver(pre_delete, sender= Image)
# def image_delete(sender, instance, **kwargs):
#     instance.image_file.delete(False)
# # post.values()[0]['text'].split()[3]

class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'
