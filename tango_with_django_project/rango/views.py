from django.shortcuts import render
from django.http import HttpResponse
from .models import Category, Page
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):
    context_dict = {}

    # Query the db for a list of all categories, order by likes, return top 5.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    context_dict = {'name': "Chris!"}

    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    # Create an empty dictionary for the template rendering engine
    context_dict = {}

    try:
        # Try to find the category name from the slug
        # using the get method: returns one model instance or exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve pages matching the category
        pages = Page.objects.filter(category=category)

        # Add the pages results in the 'pages' context dict
        # and the category objects from the db to the 'category' context dict.
        # We will use this in the template to verify that the category exists
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)


# This function can do 3 things:
#   1) showing a new blank form for adding a category
#   2) saving from data (provided by the user) to the associated model
#      and rendering a page
#   3) provide error info - if any
def add_category(request):
    # Create a CategoryForm variable
    form = CategoryForm()

    # Is it a HTTP POST?
        # An HTTP POST submits data from the client's browser to be submitted.
        # There is also HTTP GET. We use GET to retrieve
        #   a particular resource (webpage/image/file)
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Create Category object (cat) and save new category in the db
            cat = form.save(commit=True)
            # Here we could give a confirmation message,
            # but we will redirect the user to the index page.
            return index(request)
        else:
            # If the form contained errors, print to terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                # probably better to use a redirect here.
            return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form':form, 'category': category}

    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        # Try to get data from both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If both are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the db
            user = user_form.save()
            # Hash the password
            user.set_password(user.password)
            # Update the user object
            user.save()

            # UserProfile instance. Once we have created
            # a User instance, we reference it in the UserProfile instance (here)
            profile = profile_form.save(commit=False)
            profile.user = user

            # If user provided profile picture,
            # get it from the form and put it in the UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            # Update registered variable
            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', {'user_form': user_form,
                                                   'profile_form': profile_form,
                                                   'registered': registered})
