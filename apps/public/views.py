from django.shortcuts import render


def about_view(request):
    """
    About Page
    """
    return render(request, 'about.html')
