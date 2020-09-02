from django.shortcuts import render

from django.views import View

# Create your views here.

def make_context(**kwargs):
    context = {'tmp': "qweqwe qweqwe"}
    # try:
    #     settings = models.Settings.objects.get()
    # except:
    #     context = {}
    # else:
    #     context = {'settings': settings}
    if kwargs:
        for k, v in kwargs.items():
            context[f'{k}'] = v
    return context

class Index(View):
    def get(self, request):

        context = make_context()
        return render(request, 'index.html', context=context)
