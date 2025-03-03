from django.conf.urls.static import static
from django.urls import path

from chat.views import RegisterFormView, LoginFormView, UserListView, ChatView
from root import settings

urlpatterns = [
                  # path('chat', ChatTemplateView.as_view(), name='chat'),
                  # path('<str:room_name>/', ChatRoomView.as_view(), name='room'),
                  path('', RegisterFormView.as_view(), name='register'),
                  path('login', LoginFormView.as_view(), name='login'),
                  path('users', UserListView.as_view(), name='user-list'),
                  path('chat/<str:username>/', ChatView.as_view(), name='chat'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
