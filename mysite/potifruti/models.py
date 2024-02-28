from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Funcionario(models.Model):
    idfuncionario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, blank=True)
    email = models.EmailField(max_length=254)

    def __str__(self):
        return self.nome

class Cotacaoproduto(models.Model):
    idcotacaoproduto = models.AutoField(primary_key=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    produto = models.ForeignKey("Produto", on_delete=models.CASCADE)
    cotacao = models.ForeignKey("Cotacao", on_delete=models.CASCADE)
    
    @receiver(post_save, sender='potifruti.Cotacaoproduto')
    def update_produto_preco(sender, instance, **kwargs):
        instance.produto.preco = instance.preco
        instance.produto.save()
    
    def __str__(self):
        return self.produto.nome
    
class Produto(models.Model):
    idproduto = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='static/img', null=True, blank=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(max_length=150, null=True, blank=True)
    categorias = models.ManyToManyField("Categoria", blank=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.nome
    
class Categoria(models.Model):
    idcategoria = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=30, unique=True)
    produtos = models.ManyToManyField(Produto, blank=True)

    def __str__(self):
        return self.nome

class Item(models.Model):
    iditem = models.AutoField(primary_key=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    pedido = models.ForeignKey("Pedido", on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    descricao = models.CharField(max_length=100, blank=True, null=True)
    observacao = models.CharField(max_length=100, blank=True, null=True)
    
    def get_preco(self):
        cotacaoproduto = Cotacaoproduto.objects.filter(produto=self.produto, cotacao=self.pedido.cotacao).last()
        return cotacaoproduto.preco if cotacaoproduto else None


    def set_preco(self, novo_preco):
        cotacaoproduto, created = Cotacaoproduto.objects.get_or_create(produto=self.produto, cotacao=self.pedido.cotacao)
        if cotacaoproduto:
            cotacaoproduto.preco = novo_preco
            cotacaoproduto.save()
            self.save()

    @property
    def preco(self):
        cotacaoproduto = Cotacaoproduto.objects.filter(produto=self.produto, cotacao=self.pedido.cotacao).last()
        if cotacaoproduto:
            return cotacaoproduto.preco
        return None

    @preco.setter
    def preco(self, novo_preco):
        cotacaoproduto = Cotacaoproduto.objects.filter(produto=self.produto, cotacao=self.pedido.cotacao).last()
        if cotacaoproduto:
            cotacaoproduto.preco = novo_preco
            cotacaoproduto.save()
            self.save()
            
    @property
    def subtotal(self):
        if self.preco is not None and self.quantidade is not None:
            return self.quantidade * self.preco
        else:
            return 0

    def __str__(self):
        return self.produto.nome

class Pedido(models.Model):
    idpedido = models.AutoField(primary_key=True)
    datahora = models.DateTimeField(auto_now_add=True)
    precototal = models.DecimalField(default=0.00, max_digits=100, decimal_places=2, blank=True, null=True)
    cotacao = models.ForeignKey("Cotacao", on_delete=models.PROTECT, null=True, blank=True)
    cliente = models.ForeignKey("Cliente", on_delete=models.PROTECT, related_name='pedidos')
    carrinho = models.BooleanField(default=True)
     
    @property
    def precototal(self):
        total = 0
        for item in self.item_set.all():
            total += item.subtotal
        return total

    def precototal(self):
        return sum(item.subtotal for item in self.item_set.all())

    def __str__(self):
        return self.cliente.nome

class Cotacao(models.Model):
    idcotacao = models.AutoField(primary_key=True)
    datahora = models.DateTimeField(auto_now_add=True)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.funcionario.nome} - Cotacao {self.idcotacao}"

class Cliente(models.Model):
    idcliente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    cpf = models.CharField(max_length=11, blank=True)
    cnpj = models.CharField(max_length=14, blank=True)
    endereco = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)
    
    def __str__(self):
        return self.nome