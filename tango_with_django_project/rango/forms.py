from django import forms
from django.contrib.auth.models import User
from .models import Page, Category, UserProfile


# This is a helper class that allows to create Django Form from an existing model (here: Category)
class CategoryForm(forms.ModelForm):
    # Provide fields for the users to fill
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    # Hidden fields, the user won't see them but it will still be initiated to 0 & False
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Provide additional information oon the form.
    # !!! IMPORTANT: define which model we are providing the form for !!!
    class Meta:
        # Association between the ModelForm and the model itself
        model = Category
        # Association between the fields on the form and the model
        fields = ('name',)


# Similar class to the above
class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        # We can specify which fields are in the form with excluding those that we don't want
        exclude = ('category',)

    # In case user input is not correct we override the clean() method in ModelForm.
    # This method is called before saving form data to a new model instance,
    # so here we can verify and fix "bad" user input.
    # Check the value retrieved from each field of the form, try to fix it and reassign it
    # to the cleaned_data dictionary.
    # ALWAYS return the reference to the cleaned_data dictionary in the end or changes won't be applied
    def clean(self):
        # .clean_data is a dictionary attribute of ModelForm
        cleaned_data = self.cleaned_data
        # We can take data from the cleaned_data dictionary by using the get() method
        url = cleaned_data.get('url')

        # If the url is not empty and doesn't start with 'http://', add 'http://' to it
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')