from django.contrib import admin
from .models import Pedido, Cliente, Funcionario, Produto, Categoria, Cotacao, Cotacaoproduto, Item


class PedidoAdmin(admin.ModelAdmin):
    list_display=('idpedido', 'nomecliente','datahora','carrinho','cotacao')
    def idcotacao(self,obj):
        return (obj.cotacao.idcotacao)
    def nomecliente(self,obj):
        return (obj.cliente.nome)
admin.site.register(Pedido, PedidoAdmin)

class CotacaoAdmin(admin.ModelAdmin):
    list_display=('idcotacao', 'funcionario','datahora')   
admin.site.register(Cotacao,CotacaoAdmin)

class CotacaoprodutoAdmin(admin.ModelAdmin):
    list_display=('produto', 'preco','idcotacao')
    
    def idcotacao(self,obj):
        return (obj.cotacao.idcotacao)
admin.site.register(Cotacaoproduto, CotacaoprodutoAdmin)

class ItemAdmin(admin.ModelAdmin):
    list_display=('produtonome','idpedido')
    def idpedido(self,obj):
        return (obj.pedido.idpedido)
    def produtonome(self,obj):
        return (obj.produto.nome)
admin.site.register(Item, ItemAdmin)

class ClienteAdmin(admin.ModelAdmin):
    readonly_fields=('usuario',)
    list_display=('idcliente', 'nome', 'endereco', 'email')
    
    def save_model(self, request, obj, form, change):
        usuariolog = request.user
        obj.user = usuariolog
        return super(ClienteAdmin).save_model(request, obj, form, change) 
'''
        qs = super(ClienteAdmin, self).get_queryset(request)
        qs = qs.filter(usuario=request.user)
        return qs
'''
admin.site.register(Cliente, ClienteAdmin)

class FuncionarioAdmin(admin.ModelAdmin):
    list_display=('idfuncionario','nome','email')
admin.site.register(Funcionario, FuncionarioAdmin)

admin.site.register(Produto)
admin.site.register(Categoria)