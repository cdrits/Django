from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Category, Page
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .webhose_search import run_query


def index(request):
    # testing cookies
    request.session.set_test_cookie()

    context_dict = {}
    # Query the db for a list of all categories, order by likes, return top 5.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    # Obtain our Response object early so we can add cookie information.
    response = render(request, 'rango/index.html', context_dict)

    return response


def about(request):
    # Cookie testing
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    context_dict = {}
    context_dict ['name'] = 'Chris'
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/about.html', context=context_dict)

    return response


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
@login_required
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


@login_required
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
            print(form.cleaned_data)

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


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to see if the username/password combination is valid
        # & create a User object if yes.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(reverse('rango:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/user_login.html', {})


@login_required
def restricted(request):
    context_dict = {}
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango:index'))


# NOTE: all cookie values are returned as strings
# Request to get information from cookie, response to update it
def visitor_cookie_handler(request):
    # Get the number of visit cookie with COOKIES.get().
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))

    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        # Set the last visit cookie
        # (if the cookie does not exist, the set_cookie method(name_of_cookie, value_of_cookie)
        # will create one.)
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return  render(request, 'rango/search.html', {'result_list': result_list})