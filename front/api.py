from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View

from front import models
from front.views import ContextViewMixin


class AccountDeny(View):
    def get(self, request, uuid, login):
        return_url = "/accountdeny"
        log = models.Logging.objects.create(action="Удаление профиля по API", input_data=f"{login}\n{uuid}")
        try:
            account = models.Account.objects.get(uuid=uuid)
        except  models.Account.MultipleObjectsReturned:
            account = models.Account.objects.filter(uuid=uuid, user__email=login).first()
            if account:
                account.user.delete()
                log.result = log.SUCCESS
                log.save()
            else:
                log.result = log.FAIL
                log.output_data = "пользователь по параметрам удаления не найден"
                log.save()
                return HttpResponseRedirect(f'{return_url}')
        except Exception as err:
            log.result = log.FAIL
            log.output_data = f"{err}"
            log.save()
        else:
            account.user.delete()
            log.result = log.SUCCESS
            log.save()
        return HttpResponseRedirect(f'{return_url}')

class RenderDeny(ContextViewMixin):
    def get(self, request):
        form_html = get_template('includes/account_deny.html').render(context={},
                                                                  request=request)
        context = self.make_context(form_html=form_html, title='Сброс пароля')
        return render(request, "auth.html", context)