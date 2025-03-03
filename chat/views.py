from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView

from chat.forms import RegisterModelForm, LoginForm
from chat.models import CustomUser, Message


# class ChatTemplateView(TemplateView,LoginRequiredMixin):
#     template_name = 'chat/index.html'
#
# class ChatRoomView(View,LoginRequiredMixin):
#     template_name = 'chat/room.html'
#     def get(self, request,room_name):
#         return render(request,self.template_name,{"room_name":room_name} )
#




################################# auth
class RegisterFormView(FormView):
    form_class = RegisterModelForm
    template_name = "auth/register.html"
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return redirect('register')




class LoginFormView(FormView):
    form_class = LoginForm
    template_name = "auth/login.html"
    success_url = reverse_lazy('user-list')
    def form_valid(self, form):
        if form.is_valid():
            username = form.data['username']
            password = form.data['password']
            user = CustomUser.objects.filter(username=username).first()
            if user:
                if user.check_password(password):
                    login(self.request, user)
                    return super().form_valid(form)
                else:
                    return render(self.request,'auth/login.html',{'errors': "Parol xato"})
            else:
                return render(self.request, 'auth/login.html', {'errors': "Bunday foydalanuvchi nomi hali ruyxatdan utmagan!"})



################################# Home
class UserListView(ListView,LoginRequiredMixin):
    model = CustomUser
    queryset = CustomUser.objects.all()
    template_name = 'chat/users.html'
    context_object_name = 'users'

    def get_queryset(self):
        query =  super().get_queryset()
        query = query.exclude(id=self.request.user.id)
        return query


class ChatView(LoginRequiredMixin,View):
    template_name = 'chat/chat.html'

    def get(self,request, username):
        other_user = get_object_or_404(CustomUser, username=username)
        messages = Message.objects.filter(
            from_user__in=[request.user, other_user],
            receiver_user__in=[request.user, other_user]
        ).order_by("timestamp")
        return render(request, 'chat/chat.html', {'other_user': other_user,'messages': messages,})
