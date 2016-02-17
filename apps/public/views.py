from django.shortcuts import render

def main(request):
    '''
    Public facing web page.
    '''
    return render(request, 'public.html')