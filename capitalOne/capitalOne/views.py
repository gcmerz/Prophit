from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
import account.views, capitalOne.forms, json 


class SignupView(account.views.SignupView):
    """for now, this form is disabled"""

    form_class = capitalOne.forms.SignupForm

    def after_signup(self, form):
        self.create_profile(form)
        super(SignupView, self).after_signup(form)

    def create_profile(self, form):
        pass
        # profile = self.created_user.profile.first()
        # profile.api_key = form.cleaned_data['api_key']
        # profile.customer_id = form.cleaned_data['customer_id']
        # profile.save()


def homepageview(request): 
    context = {}
    if request.user.is_authenticated(): 
        transcations = Transaction.objects.filter(payer__user=request.user).order_by('-date')
        context['transactions'] = transcations
        recommendations = Recommendation.objects.select_related('merchant').filter(obsolete = False, profile__user = request.user).order_by('-score')
        context['recommendations'] = recommendations
        ps = Profile.objects.filter(user=request.user)
        if ps:
        	context['profile'] = ps[0]
    return render(request, 'homepage.html', context)


def get_vis_data(request):
    """return top 5 merchants"""
    data = {}
    amounts = []
    # loop through all merchants spent at
    for m in Merchant.objects.filter(transactions__in = Transaction.objects.filter(payer__user=request.user)):
        # get total spent at each merchant
        total_spent = 0
        for t in m.transactions.all():
            total_spent += t.amount

        amounts.append((m.name, total_spent))

    # sort list by amount spent
    sorted(amounts, key=lambda x: x[1])

    # put top five (or less) in data
    top = amounts
    if len(amounts) > 5:
        top = amounts[-5:]
    for m in top:
        data[m[0]] = m[1]

    return HttpResponse(json.dumps(data))

