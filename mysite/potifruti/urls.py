from django.urls import path
from . import views
from .views import index, detalheproduto, listapedidos, pedidodecompras, gerenciarcotacao

app_name = 'potifruti'

urlpatterns = [
    path('', index, name='index'),
    path('detalheproduto/<int:produto_id>/', detalheproduto, name='detalheproduto'),
    path('pedidos/', listapedidos, name='listapedidos'),
    path('pedidodecompras/<int:produto_id>/', pedidodecompras, name='pedidodecompras'),
    path('pedidocarrinho/', views.pedidocarrinho, name='pedidocarrinho'),
    path('gerenciarcotacao/<int:cotacao_id>/', gerenciarcotacao, name='gerenciarcotacao'),
]