from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from datetime import date

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Diário")
    stock_total = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
    
    def __str__(self):
        return self.nome
    
    def stock_disponivel(self):
        # Soma a quantidade de itens deste produto em alugueres NÃO devolvidos
        alugados = self.itemaluguer_set.filter(aluguer__devolvido=False).aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        return self.stock_total - alugados

# 1. O "CABEÇALHO" DO ALUGUER (Dados do Cliente e Datas)
class Aluguer(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_aluguer = models.DateField(default=date.today)
    data_prevista_devolucao = models.DateField()
    devolvido = models.BooleanField(default=False)
    
    # NOVO CAMPO:
    uso_interno = models.BooleanField(default=False, verbose_name="Uso Interno / Empresa")

    class Meta:
        verbose_name = "Aluguer"
        verbose_name_plural = "Alugueres"
    
    def __str__(self):
        tipo = " (INTERNO)" if self.uso_interno else ""
        return f"Aluguer #{self.id} - {self.cliente}{tipo}"

    def total_geral(self):
        # Se for uso interno, o total é sempre 0
        if self.uso_interno:
            return 0
            
        total = 0
        for item in self.itens.all():
            total += item.preco_parcial()
        return total

    def dias_aluguer(self):
        if self.data_prevista_devolucao and self.data_aluguer:
            delta = self.data_prevista_devolucao - self.data_aluguer
            return delta.days if delta.days > 0 else 1
        return 0

class ItemAluguer(models.Model):
    aluguer = models.ForeignKey(Aluguer, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Item do Aluguer"
        verbose_name_plural = "Itens do Aluguer"

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    def preco_parcial(self):
        # Se o aluguer pai for interno, o preço da linha é 0
        if self.aluguer.uso_interno:
            return 0
            
        dias = self.aluguer.dias_aluguer()
        return dias * self.produto.preco_diaria * self.quantidade

    def clean(self):
        # ... (Mantém a tua lógica de validação de stock aqui igualzinha ao que tinhas) ...
        # Copia o conteúdo do método clean() anterior para aqui.
        if self.aluguer.devolvido:
            return
        outros_itens = ItemAluguer.objects.filter(
            produto=self.produto, 
            aluguer__devolvido=False
        ).exclude(id=self.id)
        ocupados = outros_itens.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        disponivel = self.produto.stock_total - ocupados
        if self.quantidade > disponivel:
            raise ValidationError(f"Stock insuficiente para {self.produto.nome}. Só restam {disponivel}.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Bundle(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Kit")
    descricao = models.TextField(blank=True, verbose_name="Descrição")

    def __str__(self):
        return self.nome

class ItemBundle(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, related_name='itens_do_kit')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"