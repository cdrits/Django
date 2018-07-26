from django import forms
from .models import Page, Category


# This is a helper class that allows to create Django Form from an existing model (here: Category)
class CategoryForm:
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
