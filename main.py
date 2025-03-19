import tkinter as tk  # Importa o módulo tkinter com o alias 'tk' para criar interfaces gráficas.
from tkinter import ttk  # Importa o submódulo ttk do tkinter, que fornece widgets temáticos.

class TrieNode:
    """
    Classe que representa um nó na estrutura Trie.
    Cada nó contém:
    - children: um dicionário que mapeia caracteres para seus nós filhos.
    - is_end: um booleano que indica se o nó corresponde ao final de uma palavra.
    - min_distance: a menor distância restante até o final de uma palavra a partir deste nó.
    """
    def __init__(self):
        self.children = {}  # Inicializa o dicionário de filhos como vazio.
        self.is_end = False  # Inicializa is_end como False, indicando que não é o final de uma palavra.
        self.min_distance = float('inf')  # Define a menor distância como infinita inicialmente.

class WeightedTrie:
    """
    Classe que representa uma Trie ponderada.
    Fornece métodos para inserir palavras e obter sugestões com base em um prefixo.
    """
    def __init__(self):
        self.root = TrieNode()  # Inicializa a raiz da Trie com um TrieNode vazio.
    
    def insert(self, word: str) -> None:
        """
        Insere uma palavra na Trie.
        Para cada caractere na palavra, atualiza ou adiciona nós filhos conforme necessário.
        Também atualiza a menor distância restante (min_distance) em cada nó.
        """
        node = self.root
        length = len(word)  # Obtém o comprimento da palavra.
        
        for i, char in enumerate(word):
            remaining = length - i  # Calcula a distância restante até o final da palavra.
            node.min_distance = min(node.min_distance, remaining)  # Atualiza min_distance no nó atual.
            
            if char not in node.children:
                node.children[char] = TrieNode()  # Adiciona um novo nó filho se o caractere não existir.
            node = node.children[char]
        
        node.is_end = True  # Marca o final da palavra.
        node.min_distance = 0  # A distância restante no final da palavra é zero.
    
    def _collect_suggestions(self, node, current_prefix, suggestions):
        """
        Método recursivo que coleta todas as palavras a partir de um determinado nó.
        Adiciona cada palavra encontrada à lista de sugestões com seu comprimento.
        """
        if node.is_end:
            suggestions.append((current_prefix, len(current_prefix)))  # Adiciona a palavra atual às sugestões.
            
        for char, child in node.children.items():
            self._collect_suggestions(child, current_prefix + char, suggestions)  # Chama recursivamente para cada filho.
    
    def get_suggestions(self, prefix: str) -> list:
        """
        Retorna uma lista de sugestões de palavras que começam com o prefixo fornecido.
        As sugestões são ordenadas pela menor distância e, em caso de empate, em ordem alfabética.
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []  # Se o prefixo não for encontrado, retorna uma lista vazia.
            node = node.children[char]
        
        suggestions = []
        self._collect_suggestions(node, prefix, suggestions)  # Coleta todas as palavras que começam com o prefixo.
        
        # Ordena as sugestões por: 1. Menor distância até o final da palavra 2. Ordem alfabética
        suggestions.sort(key=lambda x: (len(x[0]) - len(prefix), x[0]))
        return [word for word, _ in suggestions]  # Retorna apenas as palavras, sem os comprimentos.

class AutocompleteDashboard:
    def __init__(self):
        self.trie = WeightedTrie()
        self.load_sample_data()
        
        self.window = tk.Tk()
        self.window.title("AutoCompletar Inteligente")
        self.window.geometry("500x400")
        self.window.resizable(True, True)
        self.configure_styles()
        
        self.create_widgets()
        self.setup_placeholder()
    
    def configure_styles(self):
        """Configura os estilos visuais da interface"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Cores personalizadas
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        
        self.style.configure('TEntry', 
                           font=('Arial', 12), 
                           padding=5)
        
        self.style.configure('TLabel', 
                           font=('Arial', 14, 'bold'), 
                           background=self.bg_color,
                           foreground=self.primary_color)
        
        self.window.configure(bg=self.bg_color)
    
    def load_sample_data(self):
        """
        Carrega palavras de um arquivo de texto e as insere na Trie.
        """
        path = "data\palavras-br.txt"  # Caminho para o arquivo de palavras.
        with open(path, "r", encoding="utf-8") as arquivo:
            words = [linha.strip() for linha in arquivo if linha.strip()]  # Lê e limpa cada linha do arquivo.

        for word in words:
            self.trie.insert(word)  # Insere cada palavra na Trie.
    
    def create_widgets(self):
        """Cria e organiza os componentes da interface."""
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(main_frame, 
                              text="Sistema de AutoCompletar")
        title_label.pack(pady=10)
        
        # Campo de busca
        self.search_frame = ttk.Frame(main_frame)
        self.search_frame.pack(fill='x')
        
        self.entry = ttk.Entry(self.search_frame, 
                             width=40, 
                             style='TEntry')
        self.entry.pack(side='left', fill='x', expand=True)
        
        # Botão de limpar
        clear_btn = ttk.Button(self.search_frame, 
                             text="×", 
                             width=3, 
                             command=self.clear_search)
        clear_btn.pack(side='left', padx=5)
        
        # Lista de sugestões
        self.suggestions_frame = ttk.Frame(main_frame)
        self.suggestions_frame.pack(fill='both', expand=True, pady=10)
        
        self.listbox = tk.Listbox(self.suggestions_frame,
                                width=40,
                                height=8,
                                font=('Arial', 11),
                                bg="white",
                                selectbackground=self.secondary_color,
                                activestyle='none')
        self.listbox.pack(fill='both', expand=True)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(self.suggestions_frame,
                                orient='vertical',
                                command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.entry.bind("<KeyRelease>", self.update_suggestions)
        self.entry.bind("<Return>", self.select_suggestion)
        self.listbox.bind("<Double-Button-1>", self.select_suggestion)
    
    def setup_placeholder(self):
        """Configura texto placeholder no campo de busca"""
        self.placeholder_text = "Digite para buscar..."
        self.entry.insert(0, self.placeholder_text)
        self.entry.configure(foreground='grey')
        
        self.entry.bind("<FocusIn>", self.remove_placeholder)
        self.entry.bind("<FocusOut>", self.add_placeholder)
    
    def remove_placeholder(self, event=None):
        """Remove o texto placeholder"""
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, tk.END)
            self.entry.configure(foreground='black')
    
    def add_placeholder(self, event=None):
        """Adiciona o texto placeholder se o campo estiver vazio"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder_text)
            self.entry.configure(foreground='grey')
    
    def clear_search(self):
        """Limpa o campo de busca e as sugestões"""
        self.entry.delete(0, tk.END)
        self.listbox.delete(0, tk.END)
        self.add_placeholder()
    
    def update_suggestions(self, event):
        """
        Atualiza a lista de sugestões com base no texto atual do campo de entrada.
        """
        prefix = self.entry.get()  # Obtém o texto atual do campo de entrada.
        self.listbox.delete(0, tk.END)  # Limpa todas as entradas da lista.
        
        suggestions = self.trie.get_suggestions(prefix)  # Obtém sugestões da Trie.
        for suggestion in suggestions[:8]:  # Limita a exibição a até 8 sugestões.
            self.listbox.insert(tk.END, suggestion)  # Adiciona cada sugestão à lista.
    
    def select_suggestion(self, event=None):
        """Seleciona a sugestão escolhida pelo usuário"""
        selection = self.listbox.curselection()
        if selection:
            selected_text = self.listbox.get(selection[0]).split(' (')[0]
            self.entry.delete(0, tk.END)
            self.entry.insert(0, selected_text)
            self.entry.configure(foreground='black')
    
    def run(self):
        """Executa a aplicação"""
        self.window.mainloop()

if __name__ == "__main__":
    dashboard = AutocompleteDashboard()  # Cria uma instância do painel de autocompletar.
    dashboard.run()  # Executa a aplicação.
