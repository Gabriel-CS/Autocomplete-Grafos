import tkinter as tk
from tkinter import messagebox
import math

# Dicionário global para mapear os IDs dos nós do canvas com os nós da Trie.
node_objects = {}

# Classe que representa um nó da Trie.
class TrieNode:
    def __init__(self, char=''):  # char: valor da letra para este nó
        self.char = char
        self.children = {}  # dicionário: letra -> TrieNode
        self.is_end = False
        self.x = None
        self.y = None

# Função para inserir uma palavra na Trie.
def insert_word(root, word):
    node = root
    for letter in word:
        if letter not in node.children:
            node.children[letter] = TrieNode(letter)
        node = node.children[letter]
    node.is_end = True

# Lê o arquivo e constrói a Trie.
def build_trie_from_file(filename):
    root = TrieNode()
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word:  # ignora linhas vazias
                insert_word(root, word)
    return root

# Variável global para posicionamento dos nós folhas.
global_counter = 0
def layout_trie(node, depth=0):
    global global_counter
    node.y = depth  # Profundidade determina a coordenada y

    if not node.children:
        # Nó folha: posiciona com o contador
        node.x = global_counter
        global_counter += 1
    else:
        # Processa os filhos (ordenados alfabeticamente para consistência)
        for letter in sorted(node.children.keys()):
            layout_trie(node.children[letter], depth + 1)
        # Posiciona o nó atual no centro dos filhos
        child_xs = [child.x for child in node.children.values()]
        node.x = sum(child_xs) / len(child_xs)

# Calcula os limites da árvore para definir o scrollregion.
def compute_bounds(node):
    bounds = [float('inf'), float('-inf'), float('inf'), float('-inf')]  # [min_x, max_x, min_y, max_y]
    def rec(n):
        nonlocal bounds
        bounds[0] = min(bounds[0], n.x)
        bounds[1] = max(bounds[1], n.x)
        bounds[2] = min(bounds[2], n.y)
        bounds[3] = max(bounds[3], n.y)
        for child in n.children.values():
            rec(child)
    rec(node)
    return bounds

# Função chamada ao clicar em um nó (com clique esquerdo).
def on_node_click(event):
    current_item = event.widget.find_withtag("current")[0]
    node = node_objects.get(current_item)
    if node:
        info = (f"Nó:\n"
                f"Letra: {node.char if node.char else 'Raiz'}\n"
                f"É fim de palavra: {node.is_end}\n"
                f"Número de filhos: {len(node.children)}")
        messagebox.showinfo("Informações do Nó", info)

# Função para iniciar o pan (clique direito).
def on_start_pan(event):
    event.widget.scan_mark(event.x, event.y)

# Função para efetuar o pan (clique direito arrastado).
def on_pan_motion(event):
    event.widget.scan_dragto(event.x, event.y, gain=1)

# Função para desenhar a árvore na tela usando tkinter.
def draw_trie(canvas, node, parent_coords=None, parent_letter=None,
              x_scale=60, y_scale=60, node_radius=15):
    # Converte as coordenadas calculadas para pixels.
    x = node.x * x_scale + 50   # offset para margem
    y = node.y * y_scale + 50

    # Se há conexão com nó pai, desenha a aresta e a letra
    if parent_coords is not None:
        # Calcula a direção da linha
        dx = x - parent_coords[0]
        dy = y - parent_coords[1]
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            start_x, start_y = parent_coords[0], parent_coords[1]
            end_x, end_y = x, y
        else:
            # Define os pontos na borda dos círculos
            start_x = parent_coords[0] + (node_radius * dx / dist)
            start_y = parent_coords[1] + (node_radius * dy / dist)
            end_x = x - (node_radius * dx / dist)
            end_y = y - (node_radius * dy / dist)
        
        # Desenha a linha sem seta
        canvas.create_line(start_x, start_y, end_x, end_y)
        
        # Calcula o ponto médio da linha
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2

        # Parâmetros da seta
        arrow_length = 10  # comprimento da seta
        arrow_width = 6    # largura da base da seta

        # Ângulo da linha
        angle = math.atan2(dy, dx)

        # Calcula o ponto da ponta da seta (apontando para o filho)
        tip_x = mid_x + (arrow_length/2) * math.cos(angle)
        tip_y = mid_y + (arrow_length/2) * math.sin(angle)
        
        # Calcula os pontos da base (esquerda e direita)
        left_x = mid_x - (arrow_length/2) * math.cos(angle) + (arrow_width/2) * math.sin(angle)
        left_y = mid_y - (arrow_length/2) * math.sin(angle) - (arrow_width/2) * math.cos(angle)
        right_x = mid_x - (arrow_length/2) * math.cos(angle) - (arrow_width/2) * math.sin(angle)
        right_y = mid_y - (arrow_length/2) * math.sin(angle) + (arrow_width/2) * math.cos(angle)
        
        # Desenha o triângulo representando a seta
        canvas.create_polygon(tip_x, tip_y, left_x, left_y, right_x, right_y, fill="black")


    # Desenha o nó (círculo) e associa o evento de clique.
    node_id = canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius,
                                fill="#4bdb5b", outline="black", tags="node")
    node_objects[node_id] = node
    canvas.tag_bind(node_id, "<Button-1>", on_node_click)

    # Se houver uma letra associada (não é o nó raiz), desenha-a dentro do nó.
    if parent_letter is not None:
        canvas.create_text(x, y, text=parent_letter, fill="#1a4cf0", font=("Arial", 10, "bold"))
    elif node.is_end:
        # Opcional: caso queira destacar nós finais mesmo sem letra, pode exibir um asterisco.
        canvas.create_text(x, y, text="*", fill="red", font=("Arial", 10, "bold"))

    # Desenha os filhos.
    for letter, child in sorted(node.children.items()):
        draw_trie(canvas, child, parent_coords=(x, y), parent_letter=letter,
                  x_scale=x_scale, y_scale=y_scale, node_radius=node_radius)

def main():
    # Construa a Trie a partir do arquivo de palavras.
    trie_file = "data/apresentacao.txt"
    root = build_trie_from_file(trie_file)

    # Calcule o layout da Trie.
    global global_counter
    global_counter = 0
    layout_trie(root)

    # Configuração da janela e canvas com scrollbars.
    window = tk.Tk()
    window.title("Árvore Trie Interativa com Navegação")

    canvas_width = 800
    canvas_height = 600

    # Cria o canvas e as scrollbars.
    hbar = tk.Scrollbar(window, orient=tk.HORIZONTAL)
    hbar.pack(side=tk.BOTTOM, fill=tk.X)
    vbar = tk.Scrollbar(window, orient=tk.VERTICAL)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg="white",
                       xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    hbar.config(command=canvas.xview)
    vbar.config(command=canvas.yview)

    # Permite o pan com o clique direito.
    canvas.bind("<ButtonPress-3>", on_start_pan)
    canvas.bind("<B3-Motion>", on_pan_motion)

    # Desenha a Trie no canvas.
    draw_trie(canvas, root)

    # Ajusta o scrollregion para abranger toda a árvore.
    x_scale = 60
    y_scale = 60
    node_radius = 15
    bounds = compute_bounds(root)  # [min_x, max_x, min_y, max_y]
    left = bounds[0] * x_scale + 50 - node_radius
    right = bounds[1] * x_scale + 50 + node_radius
    top = bounds[2] * y_scale + 50 - node_radius
    bottom = bounds[3] * y_scale + 50 + node_radius
    canvas.config(scrollregion=(left, top, right, bottom))

    window.mainloop()

if __name__ == "__main__":
    main()