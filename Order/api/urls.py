from django.urls import path
from Order import views

urlpatterns = [
    path('orders/',views.OrderView.as_view(),name='get_or_create_order'),
    path('update/order/<str:order_id>/',views.OrderUpdateView.as_view(),name='update_order_status')
]