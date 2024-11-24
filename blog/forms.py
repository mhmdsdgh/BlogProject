from django import forms
from .models import User, Post, Comment
from django.contrib.auth.forms import AuthenticationForm
from mptt.forms import TreeNodeChoiceField


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),
    )
    message = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=250, required=True)
    email = forms.EmailField(required=False)
    phone = forms.CharField(min_length=11, max_length=11, required=True)
    subject = forms.CharField(required=True)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("")
            else:
                return phone


class CommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all(), required=False, widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'نام'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'ایمیل'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'متن دیدگاه'}))

    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) < 3:
                raise forms.ValidationError("نام کوتاه است")
            else:
                return name

    class Meta:
        model = Comment
        fields = ['name', 'parent', 'email', 'body']

# class UserForm(forms.Form):
    
#     first_name = forms.CharField(min_length=1, max_length=30, required=True, label="نام")
#     last_name = forms.CharField(max_length=30, required=False, label="نام خانوادگی")
#     user_id = forms.CharField(min_length=5, max_length=30, required=False, label="آیدی")
#     email = forms.EmailField(required=True, label="ایمیل")

#     def clean_user_id(self):
#         user_id = self.cleaned_data['user_id']
#         if user_id:
#             try:
#                 ControlUsers.objects.get(user_id=user_id)
#             except ControlUsers.DoesNotExist:
#                 return user_id
#             raise forms.ValidationError("نام کاربری قبلا استفاده شده است")

#     class Meta:
#         model = 12
#         fields = ['first_name', 'last_name', 'user_id', 'email']

# class PostForm(forms.Form):

#     author = forms.CharField(label="نویسنده")
#     title = forms.CharField(max_length=100, label="عنوان")    
#     description = forms.CharField(label="توضیحات")
#     reading_time = forms.CharField(label="زمان مطالعه (به دقیقه)")

#     class Meta:
#         model = Post
#         fields = ['author', 'title', 'description', 'reading_time']
    

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'reading_time', 'tags', 'category']


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput, label='پسورد')
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput, label="تکرار پسورد")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('پسورد ها مطابقت ندارند')
        return cd['password2']


class SearchForm(forms.Form):
    query = forms.CharField()


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=250, required=True)
    password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'date_of_birth', 'bio', 'job', 'photo',
                  'telegram', 'instagram', 'website']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError('username already exists!')
        return username
