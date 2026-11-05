from .models import Item, ItemFornecedor


class CatalogoService:
    def listar_itens(self):
        contexto = []
        itens_ativos = Item.objects.filter(ativo=True).order_by("nome")
        for item in itens_ativos:
            anuncios_ativos = ItemFornecedor.objects.filter(item=item,ativo=True).order_by("preco_atual")
            anuncios_validos = []

            for anuncio in anuncios_ativos:
                if anuncio.fornecedor.ativo:
                    anuncios_validos.append(anuncio)
            
            if len(anuncios_validos) > 0:
                contexto.append({
                    "nome": item.nome,
                    "tipo": item.tipo,
                    "imagem": item.imagem,
                    "preco": anuncios_validos[0].preco_atual,
                    "loja": anuncios_validos[0].fornecedor.nome,
                    "qtd_lojas": len(anuncios_validos),
                })

        return contexto

    
    def filtrar_itens(self, tipo=False, preco=False, nome=False):
        cards = self.listar_itens()

        if nome:
            cards.sort(key=lambda card: card["nome"])
        if preco:
            cards.sort(key=lambda card: card["preco"])
        if tipo:
            cards.sort(key=lambda card: card["tipo"])

        return cards
