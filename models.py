from django.db import models


class Item(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome")
    tipo = models.CharField(max_length=50, verbose_name="Tipo", help_text="Ex.: processador, monitor")
    imagem = models.ImageField(upload_to="itens/", blank=True, null=True, verbose_name="Imagem")
    notificar_promo = models.BooleanField(default=False, verbose_name="Notificar promoção")
    ativo = models.BooleanField(default=True, verbose_name="Ativo no catálogo")  # soft delete

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"

    @property
    def menor_preco(self):
        anuncio = self.fornecedores_item.filter(ativo=True).order_by("preco_atual").first()
        return anuncio.preco_atual if anuncio else None

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome")
    link_site = models.URLField(max_length=200, unique=True, verbose_name="Site da loja")
    ativo = models.BooleanField(default=True, verbose_name="Loja ativa")  # soft delete

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return self.nome


class ItemFornecedor(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="fornecedores_item", verbose_name="Item")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name="itens_fornecedor", verbose_name="Loja / Fornecedor")
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço atual na loja")
    link_anuncio = models.URLField(max_length=500, verbose_name="Link do anúncio específico")
    ativo = models.BooleanField(default=True, verbose_name="Anúncio ativo")  # soft delete

    class Meta:
        verbose_name = "Item no Fornecedor"
        verbose_name_plural = "Itens nos Fornecedores"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preco_original = self.preco_atual if self.pk else None

    def save(self, *args, **kwargs):
        eh_novo = self.pk is None
        preco_mudou = self.preco_atual != self._preco_original

        super().save(*args, **kwargs) #super().save(nome, tipo, link, ativo=True, context=False)

        if eh_novo or preco_mudou:
            HistoricoPreco.objects.create(
                item_fornecedor=self,
                preco=self.preco_atual
            )
            self._preco_original = self.preco_atual

    def __str__(self):
        return f"{self.item.nome} - {self.fornecedor.nome} (R$ {self.preco_atual})"


class Oferta(models.Model):
    # ligação 1: cada oferta pertence a UMA loja parceira
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name="ofertas")
    # ligação 2: uma oferta vale para VÁRIOS itens e um item pode ter VÁRIAS ofertas
    # ex: cupom de descontos / promoção do proprio site / blackfriday / etc
    itens = models.ManyToManyField(Item, related_name="ofertas", blank=True)

    nome = models.CharField(max_length=150, verbose_name="Nome")
    tipo = models.CharField(max_length=50, verbose_name="Tipo", help_text="Ex.: promoção, cupom")
    descricao = models.TextField(verbose_name="Descrição")
    imagem = models.ImageField(upload_to="ofertas/", blank=True, verbose_name="Imagem")
    notificar_promo = models.BooleanField(default=False, verbose_name="Notificar promoção")
    ativo = models.BooleanField(default=True, verbose_name="Oferta ativa")

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"

    def __str__(self):
        return self.nome


class HistoricoPreco(models.Model):
    item_fornecedor = models.ForeignKey(ItemFornecedor, on_delete=models.PROTECT, related_name="historico_precos", verbose_name="Anúncio (Item / Loja)")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço registrado")
    data = models.DateTimeField(auto_now_add=True, verbose_name="Data da coleta")

    class Meta:
        verbose_name = "Histórico de Preço"
        verbose_name_plural = "Históricos de Preços"
        ordering = ["-data"]

    def __str__(self):
        return f"{self.item_fornecedor.item.nome} na {self.item_fornecedor.fornecedor.nome}: R$ {self.preco}"