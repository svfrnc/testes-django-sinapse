from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404
from .services import CatalogoService


class HomeView(View):
    def get(self, request, *args, **kwargs):
        tipo = False
        preco = False
        nome = False

        if request.GET.get("tipo"):
            tipo = True
        if request.GET.get("preco"):
            preco = True
        if request.GET.get("nome"):
            nome = True

        if tipo or preco or nome:
            itens = CatalogoService().filtrar_itens(tipo, preco, nome)
        else:
            itens = CatalogoService().listar_itens()

        contexto = {
            "itens": itens,
            "tipo": tipo,
            "preco": preco,
            "nome": nome,
        }
        return render(request, "catalogo/home.html", context=contexto)

class HistoricoPrecoView(View):
    def get(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(Item, pk=item_id, ativo=True)
        periodos = CatalogoService().obter_periodos_menor_preco(item.id)
        contexto = {
            "item": item,
            "periodos": periodos,
        }

        return render(request, "catalogo/historico_preco.html", context=contexto) 