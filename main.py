"""João Victor Pereira Couto  RA: 24.00115-5"""

import json                              # Manipulação de arquivos JSON
import matplotlib                        # Backend não-interativo (sem display gráfico necessário)
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # Plotagem do grafo
import matplotlib.patches as mpatches   # Legendas e patches do grafo
import networkx as nx                    # Estrutura do grafo dirigido
import math                              # Cálculos de ângulo para auto-arcos


class MealyMachine:
    """Representa uma Máquina de Mealy carregada a partir de um arquivo JSON."""

    def __init__(self, arquivo):
        """Inicializa a máquina de Mealy a partir de um arquivo JSON.
        O arquivo deve conter as chaves: S, I, O, f, g, s_ini."""
        try:
            with open(arquivo, 'r') as f:
                dados = json.load(f)
        except FileNotFoundError:
            raise SystemExit("Erro: arquivo não encontrado.")
        except json.JSONDecodeError:
            raise SystemExit("Erro: arquivo JSON inválido.")

        try:
            self.S = set(dados["S"])             # Conjunto de estados
            self.I = set(dados["I"])             # Alfabeto de entrada
            self.O = set(dados["O"])             # Alfabeto de saída
            self.f = dados["f"]                  # Função de transição δ: S × I → S
            self.g = dados["g"]                  # Função de saída λ: S × I → O
            self.estado_inicial = dados["s_ini"] # Estado inicial
        except KeyError as e:
            raise SystemExit(f"Erro: campo ausente no JSON: {e}")

        if self.estado_inicial not in self.S:
            raise SystemExit("Erro: estado inicial inválido.")

    # ------------------------------------------------------------------
    # Simulação
    # ------------------------------------------------------------------

    def simular(self, entrada):
        """Simula a máquina de Mealy para uma cadeia de entrada."""
        estado = self.estado_inicial
        saida_total = ""

        print("\n--- Simulação da Máquina de Mealy ---")
        print(f"Estado inicial: {estado}")
        print(f"Entrada: {entrada}\n")

        if entrada == "":
            print("Erro: cadeia de entrada vazia!")
            return

        for c in entrada:
            if estado not in self.S:
                print(f"Erro: estado '{estado}' inválido!")
                return

            if c not in self.I:
                print(f"Erro: símbolo '{c}' não pertence ao alfabeto de entrada!")
                return

            if c not in self.f.get(estado, {}):
                print(f"Erro: não há transição para ({estado}, {c})")
                return

            proximo_estado = self.f[estado][c]

            if c not in self.g.get(estado, {}):
                print(f"Erro: saída não definida para ({estado}, {c})")
                return

            saida = self.g[estado][c]
            saida_total += saida
            print(f"({estado}, {c}) -> ({proximo_estado}, {saida})")
            estado = proximo_estado

        print(f"\nEstado final: {estado}")
        print(f"Saída: {saida_total}")

    # ------------------------------------------------------------------
    # Tabelas-verdade
    # ------------------------------------------------------------------

    def exibir_tabelas(self):
        """Exibe as tabelas de transição (δ) e de saída (λ) formatadas."""
        estados  = sorted(self.S)
        entradas = sorted(self.I)

        # Largura das colunas
        larg_est = max(len("Estado") + 1, max(len(s) + 2 for s in estados))
        larg_cel = max(max(len(e) for e in entradas), 6)
        sep = "-" * (larg_est + 2 + (larg_cel + 3) * len(entradas))

        def cabecalho():
            linha = f"{'Estado':<{larg_est}}  "
            for e in entradas:
                linha += f"| {e:^{larg_cel}} "
            return linha

        def linha_tabela(s, tabela):
            marcador = "*" if s == self.estado_inicial else " "
            linha = f"{(marcador + s):<{larg_est}}  "
            for e in entradas:
                valor = tabela.get(s, {}).get(e, "-")
                linha += f"| {valor:^{larg_cel}} "
            return linha

        # Tabela de Transição δ
        print("\n┌─────────────────────────────────────────┐")
        print("│  Tabela de Transição  δ(estado, entrada) │")
        print("└─────────────────────────────────────────┘")
        print(cabecalho())
        print(sep)
        for s in estados:
            print(linha_tabela(s, self.f))

        # Tabela de Saída λ
        print("\n┌─────────────────────────────────────────┐")
        print("│  Tabela de Saída  λ(estado, entrada)     │")
        print("└─────────────────────────────────────────┘")
        print(cabecalho())
        print(sep)
        for s in estados:
            print(linha_tabela(s, self.g))

        print(f"\n  (* = estado inicial: {self.estado_inicial})")

    # ------------------------------------------------------------------
    # Visualização do grafo
    # ------------------------------------------------------------------

    def visualizar_grafo(self, arquivo_saida="grafo_mealy.png"):
        """Gera e salva o diagrama de estados da máquina de Mealy como PNG."""

        G = nx.MultiDiGraph()
        estados = sorted(self.S)
        G.add_nodes_from(estados)

        # Agrupa rótulos de múltiplas transições entre o mesmo par de estados
        arestas: dict[tuple[str, str], list[str]] = {}
        for origem in sorted(self.f):
            for simbolo in sorted(self.f[origem]):
                destino = self.f[origem][simbolo]
                saida   = self.g.get(origem, {}).get(simbolo, "?")
                rotulo  = f"{simbolo}/{saida}"
                arestas.setdefault((origem, destino), []).append(rotulo)

        # Layout circular para os estados
        pos = nx.circular_layout(estados)

        fig, ax = plt.subplots(figsize=(9, 7))
        ax.set_title("Diagrama de Estados — Máquina de Mealy",
                     fontsize=13, fontweight="bold", pad=14)
        ax.axis("off")

        # Cores dos nós
        COR_INICIAL = "#66BB6A"   # verde para estado inicial
        COR_NORMAL  = "#64B5F6"   # azul para demais estados
        cores = [COR_INICIAL if s == self.estado_inicial else COR_NORMAL for s in estados]

        # Nós
        nx.draw_networkx_nodes(G, pos, nodelist=estados,
                               node_color=cores, node_size=1600,
                               edgecolors="#333333", linewidths=1.8, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)

        # Separa arestas normais de auto-arcos
        arestas_normais = {k: v for k, v in arestas.items() if k[0] != k[1]}
        arestas_self    = {k: v for k, v in arestas.items() if k[0] == k[1]}

        # Arestas normais
        for (origem, destino), rotulos in arestas_normais.items():
            tem_reversa = (destino, origem) in arestas_normais
            rad = 0.28 if tem_reversa else 0.0

            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(origem, destino)],
                connectionstyle=f"arc3,rad={rad}",
                arrowsize=20, arrowstyle="-|>",
                edge_color="#444444", width=1.6, ax=ax,
                min_source_margin=28, min_target_margin=28,
            )

            # Posição do rótulo deslocada perpendicularmente quando há aresta reversa
            xo, yo = pos[origem]
            xd, yd = pos[destino]
            xm = (xo + xd) / 2
            ym = (yo + yd) / 2
            if tem_reversa and rad != 0.0:
                dx, dy = xd - xo, yd - yo
                norm = math.hypot(dx, dy) or 1
                xm += -dy / norm * 0.17
                ym +=  dx / norm * 0.17

            texto = "\n".join(rotulos)
            ax.text(xm, ym, texto, fontsize=8.5, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.25", fc="white",
                              ec="#aaaaaa", alpha=0.9))

        # Auto-arcos (self-loops)
        for (estado, _), rotulos in arestas_self.items():
            x, y = pos[estado]
            raio  = 0.13
            angulo = math.atan2(y, x)   # aponta para fora do centro do layout
            cx = x + raio * math.cos(angulo)
            cy = y + raio * math.sin(angulo)

            circulo = plt.Circle((cx, cy), raio, color="#444444",
                                 fill=False, linewidth=1.6)
            ax.add_patch(circulo)

            texto = "\n".join(rotulos)
            ax.text(cx, cy + raio + 0.05, texto, fontsize=8.5,
                    ha="center", va="bottom",
                    bbox=dict(boxstyle="round,pad=0.25", fc="white",
                              ec="#aaaaaa", alpha=0.9))

        # Seta de entrada apontando para o estado inicial
        xi, yi = pos[self.estado_inicial]
        ax.annotate("", xy=(xi, yi),
                    xytext=(xi - 0.28, yi),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.8))

        # Legenda
        legenda = [
            mpatches.Patch(color=COR_INICIAL,
                           label=f"Estado inicial ({self.estado_inicial})"),
            mpatches.Patch(color=COR_NORMAL, label="Demais estados"),
        ]
        ax.legend(handles=legenda, loc="lower right", fontsize=9)

        plt.tight_layout()
        plt.savefig(arquivo_saida, dpi=130, bbox_inches="tight")
        plt.close()
        print(f"\nGrafo salvo em: {arquivo_saida}")

    # ------------------------------------------------------------------
    # Exibição resumida da definição formal
    # ------------------------------------------------------------------

    def exibir_definicao(self):
        """Exibe a definição formal da máquina."""
        print("\n--- Definição Formal ---")
        print(f"  S (estados)       : {sorted(self.S)}")
        print(f"  I (entrada)       : {sorted(self.I)}")
        print(f"  O (saída)         : {sorted(self.O)}")
        print(f"  s_ini (inicial)   : {self.estado_inicial}")


# ------------------------------------------------------------------
# Função principal
# ------------------------------------------------------------------

def main():
    """Função principal — carrega a máquina e oferece menu interativo."""
    nome_arquivo = input("Digite o nome do arquivo da máquina: ")
    maquina = MealyMachine(nome_arquivo)

    # Ao carregar, já exibe as tabelas e gera o grafo automaticamente
    maquina.exibir_definicao()
    maquina.exibir_tabelas()
    maquina.visualizar_grafo()

    while True:
        print("\n" + "=" * 42)
        print(" [1] Simular cadeia de entrada")
        print(" [2] Exibir tabelas de transição/saída")
        print(" [3] Gerar diagrama de estados (PNG)")
        print(" [s] Sair")
        print("=" * 42)
        opcao = input("Opção: ").strip().lower()

        if opcao in ("s", "sair"):
            print("Encerrando programa...")
            break
        elif opcao == "1":
            entrada = input("Digite a cadeia de entrada: ")
            maquina.simular(entrada)
        elif opcao == "2":
            maquina.exibir_tabelas()
        elif opcao == "3":
            arq = input("Nome do arquivo PNG (Enter = 'grafo_mealy.png'): ").strip()
            if not arq:
                arq = "grafo_mealy.png"
            maquina.visualizar_grafo(arq)
        else:
            print("Opção inválida. Escolha 1, 2, 3 ou s.")


if __name__ == "__main__":
    main()
