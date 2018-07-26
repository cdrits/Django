from django.shortcuts import render
from django.http import HttpResponse
from .models import Category, Page


def index(request):
    context_dict={}

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
    context_dict={}

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
        context_dict['category']= category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)