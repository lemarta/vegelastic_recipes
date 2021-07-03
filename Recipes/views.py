from django.shortcuts import render
from django.views import View


# Create your views here.


class MainPageView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request=request, template_name='base.html', context=context)