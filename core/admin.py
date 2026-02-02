from django.contrib import admin
from django.utils.html import format_html
from .models import Bundle, Cliente, ItemBundle, Produto, Aluguer, ItemAluguer
from django.urls import reverse
from django.utils.html import format_html
from django import forms

# --- CORREÇÃO AQUI ---
# Juntámos a configuração da Imagem E a da Pesquisa na mesma classe
class ProdutoAdmin(admin.ModelAdmin):
    # 1. Configuração da Lista (Tabela)
    list_display = ('imagem_preview', 'nome', 'preco_diaria', 'status_stock')
    search_fields = ('nome',)
    
    # 2. Configuração do Formulário de Edição
    # Criamos um campo de "apenas leitura" para a imagem grande
    readonly_fields = ['ver_imagem_grande']
    
    # Definimos a ordem dos campos para a imagem aparecer antes do upload
    fields = ('nome', 'ver_imagem_grande', 'imagem', 'preco_diaria', 'stock_total')

    # --- FUNÇÕES AUXILIARES ---

    # Função A: Imagem pequena para a Lista (Thumbnail)
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="width: 50px; height:auto; border-radius:3px;" />', obj.imagem.url)
        return "-"
    imagem_preview.short_description = "Foto"

    # Função B: Imagem grande para o Formulário de Edição
    def ver_imagem_grande(self, obj):
        if obj.imagem:
            # Aqui defino max-height: 300px para não ocupar o ecrã todo
            return format_html('<img src="{}" style="max-height: 300px; max-width: 100%; border-radius: 5px; border: 1px solid #ccc;" />', obj.imagem.url)
        return "Nenhuma imagem carregada"
    ver_imagem_grande.short_description = "Visualização Atual"

    # Função C: Cores do Stock (que já tinhas)
    def status_stock(self, obj):
        if obj.stock_total == 0:
            cor = 'red'; texto = f'Indisponível ({obj.stock_total})'; peso = 'bold'
        elif obj.stock_total < 3:
            cor = 'orange'; texto = f'Baixo Stock ({obj.stock_total})'; peso = 'bold'
        else:
            cor = 'green'; texto = f'Em Stock ({obj.stock_total})'; peso = 'normal'

        return format_html('<span style="color: {}; font-weight: {}">{}</span>', cor, peso, texto)
    status_stock.short_description = "Quantidade"

    # 2. Pequeno bónus: Mostrar miniatura da imagem se existir
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="width: 50px; height:auto; border-radius:5px;" />', obj.imagem.url)
        return "-"
    imagem_preview.short_description = "Foto"

    def status_stock(self, obj):
        # AQUI ESTÁ A MUDANÇA: Usamos a função .stock_disponivel() em vez do campo direto
        disponivel = obj.stock_disponivel() 
        total = obj.stock_total

        if disponivel == 0:
            cor = 'red'
            peso = 'bold'
            texto = f'Indisponível (0/{total})' # Ex: 0 livres de 10 totais
        elif disponivel < 3:
            cor = 'orange'
            peso = 'bold'
            texto = f'Restam {disponivel} (Total: {total})'
        else:
            cor = 'green'
            peso = 'normal'
            texto = f'Em Stock: {disponivel}'

        return format_html(
            '<span style="color: {}; font-weight: {}">{}</span>', 
            cor, peso, texto
        )
    
    status_stock.short_description = "Disponibilidade"

# --- INLINES ---
class ItemAluguerInline(admin.TabularInline):
    model = ItemAluguer
    extra = 1
    
    # 1. Definimos a ordem das colunas: A Imagem vem primeiro
    fields = ('imagem_preview', 'produto', 'quantidade')
    
    # 2. Como a imagem não é editável, tem de estar nos readonly_fields
    readonly_fields = ['imagem_preview']

    # 3. Função para ir buscar a imagem ao Produto relacionado
    def imagem_preview(self, obj):
        # Só tentamos mostrar imagem se o item já existir na base de dados (obj.id)
        # e se tiver um produto associado com imagem
        if obj.id and obj.produto and obj.produto.imagem:
            return format_html(
                '<img src="{}" style="width: 40px; height:auto; border-radius:3px;" />', 
                obj.produto.imagem.url
            )
        return "-"
    
    imagem_preview.short_description = "Foto"

class AluguerForm(forms.ModelForm):
    # MUDANÇA 1: Usamos ModelMultipleChoiceField em vez de ModelChoiceField
    adicionar_kits = forms.ModelMultipleChoiceField(
        queryset=Bundle.objects.all(), 
        required=False, 
        widget=forms.CheckboxSelectMultiple, # Fica com aspeto de caixinhas para marcar
        label="⚡ Adicionar Bundles (Kits)",
        help_text="Marque todos os kits que quer adicionar a este aluguer."
    )

    class Meta:
        model = Aluguer
        fields = '__all__'

class AluguerAdmin(admin.ModelAdmin):
    form = AluguerForm
    inlines = [ItemAluguerInline]
    
    list_display = ('id', 'cliente', 'data_aluguer', 'devolvido', 'uso_interno', 'mostrar_total', 'botao_imprimir')
    list_filter = ('devolvido', 'uso_interno', 'data_aluguer')
    search_fields = ('cliente__nome', 'id')

    # Ajustei o nome do campo aqui também ('adicionar_kits')
    fields = ('cliente', 'adicionar_kits', 'data_aluguer', 'data_prevista_devolucao', 'uso_interno', 'devolvido')

    def botao_imprimir(self, obj):
        url = reverse('imprimir_aluguer', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background-color:#999; color:white; padding:3px 10px; border-radius:3px;">🖨️ Imprimir</a>', 
            url
        )
    botao_imprimir.short_description = "Ações"
    
    def mostrar_total(self, obj):
        return f"{obj.total_geral()} €"
    mostrar_total.short_description = "Total"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        
        # MUDANÇA 2: Agora recebemos uma lista de kits
        kits_escolhidos = form.cleaned_data.get('adicionar_kits')
        
        if kits_escolhidos:
            aluguer = form.instance 
            
            # Loop 1: Percorre cada Kit selecionado (ex: Cozinha, Sala...)
            for kit in kits_escolhidos:
                # Loop 2: Percorre os produtos dentro desse Kit
                for item_kit in kit.itens_do_kit.all():
                    
                    # Verifica se o produto já existe neste aluguer para somar a quantidade
                    # (Isto evita ficar com 2 linhas repetidas de "Garfos")
                    item_existente = ItemAluguer.objects.filter(aluguer=aluguer, produto=item_kit.produto).first()
                    
                    if item_existente:
                        item_existente.quantidade += item_kit.quantidade
                        item_existente.save()
                    else:
                        ItemAluguer.objects.create(
                            aluguer=aluguer,
                            produto=item_kit.produto,
                            quantidade=item_kit.quantidade
                        )
                
# Não te esqueças de registar os Bundles para poderes criá-los!
class ItemBundleInline(admin.TabularInline):
    model = ItemBundle
    extra = 1

class BundleAdmin(admin.ModelAdmin):
    inlines = [ItemBundleInline]
    list_display = ('nome', 'total_itens')
    
    def total_itens(self, obj):
        return obj.itens_do_kit.count()

admin.site.register(Bundle, BundleAdmin)

admin.site.register(Cliente)
admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Aluguer, AluguerAdmin)