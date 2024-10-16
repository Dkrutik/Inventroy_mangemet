from django.urls import path
from .views import ItemListCreateView, ItemDetailView

urlpatterns = [
    path('items/', ItemListCreateView.as_view(), name='create_item'),
    path('items/<int:item_id>/', ItemDetailView.as_view(), name='item_detail'),
]