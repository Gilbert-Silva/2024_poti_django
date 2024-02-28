from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, Funcionario, Produto, Cotacao, Cotacaoproduto, Item
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Cotacaoproduto)
def update_produto_preco(sender, instance, **kwargs):
    instance.produto.preco = instance.preco
    instance.produto.save()

def index(request):
    produtos = Produto.objects.all()
    context = {
        'produtos': produtos
    }
    return render(request, 'potifruti/index.html', context)

def detalheproduto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    context = {
        'produto': produto
    }
    return render(request, 'potifruti/detalheproduto.html', context)

def listapedidos(request):
    pedidos = Pedido.objects.all()

    for pedido in pedidos:
        for item in pedido.item_set.all():
            cotacaoproduto = item.produto.cotacaoproduto_set.filter(cotacao=item.pedido.cotacao).last()
            item.preco = cotacaoproduto.preco if cotacaoproduto else None

    context = {'pedidos': pedidos}
    return render(request, 'potifruti/pedido.html', context)

def pedidodecompras(request):
    ultimo_pedido = Pedido.objects.filter(cliente=request.user.cliente, carrinho=True).last()

    if request.method == 'POST':
        quantidade = int(request.POST.get('quantidade', 1))

        if ultimo_pedido is None or not ultimo_pedido.carrinho:
            ultimo_pedido = Pedido.objects.create(cliente=request.user.cliente, carrinho=True)

        item, created = Item.objects.get_or_create(produto=produto, pedido=ultimo_pedido)
        if not created:
            item.quantidade += quantidade
            item.save()

        return redirect('potifruti:detalheproduto', produto_id=produto_id)

    itens_pedido = Item.objects.filter(pedido=ultimo_pedido)
    context = {'produto': produto, 'itens_pedido': itens_pedido}
    return render(request, 'potifruti/pedidodecompras.html', context)

def pedidocarrinho(request):
    pedidos_carrinho = Pedido.objects.filter(carrinho=True)
    cotacoes_copiadas = []

    if request.method == 'POST':
        funcionario = Funcionario.objects.first()
        nova_cotacao = Cotacao.objects.create(funcionario=funcionario)

        produtos_adicionados = set()

        for pedido in pedidos_carrinho:
            for item in pedido.item_set.all():
                if item.produto.idproduto not in produtos_adicionados:
                    cotacaoproduto = Cotacaoproduto.objects.create(
                        cotacao=nova_cotacao,
                        produto=item.produto,
                        preco=item.get_preco()
                    )
                    cotacoes_copiadas.append(cotacaoproduto)
                    produtos_adicionados.add(item.produto.idproduto)

        pedidos_carrinho.update(cotacao=nova_cotacao)

        return redirect('potifruti:gerenciarcotacao', cotacao_id=nova_cotacao.idcotacao)

    context = {
        'pedidos': pedidos_carrinho,
        'cotacoes_copiadas': cotacoes_copiadas,
    }

    return render(request, 'potifruti/pedidocarrinho.html', context)

def gerenciarcotacao(request, cotacao_id):
    cotacao = get_object_or_404(Cotacao, idcotacao=cotacao_id)
    pedidos_carrinho = Pedido.objects.filter(carrinho=True)

    itens_cotacao_dict = {}

    for pedido in pedidos_carrinho:
        itens_pedido = Item.objects.filter(
            pedido=pedido,
            pedido__cotacao=cotacao
        ).distinct()

        for item in itens_pedido:
            itens_cotacao_dict[item.produto.idproduto] = item

    itens_cotacao = list(itens_cotacao_dict.values())
    
    if request.method == 'POST':
        for item in itens_cotacao:
            novo_preco_str = request.POST.get(f'novo_preco_{item.iditem}')
            if novo_preco_str is not None:
                novo_preco = float(novo_preco_str)
                cotacaoproduto, created = Cotacaoproduto.objects.get_or_create(produto=item.produto, cotacao=cotacao)
                cotacaoproduto.preco = novo_preco
                cotacaoproduto.save()
                
        todos_itens_atualizados = all(Cotacaoproduto.objects.filter(produto=item.produto, cotacao=cotacao).exists() for item in itens_cotacao)
        if todos_itens_atualizados:
            pedido.carrinho = False
            pedido.save()
    
    context = {
        'cotacao': cotacao,
        'itens_cotacao': itens_cotacao
    }

    return render(request, 'potifruti/gerenciarcotacao.html', context)