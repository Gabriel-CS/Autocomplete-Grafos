import tkinter as tk
from tkinter import ttk
import unicodedata
from collections import defaultdict

class TrieNode:
    """
    Classe que representa um nó na estrutura Trie.
    Cada nó contém:
    - children: um dicionário que mapeia caracteres para seus nós filhos.
    - is_end: um booleano que indica se o nó corresponde ao final de uma palavra.
    - min_distance: a menor distância restante até o final de uma palavra a partir deste nó.
    """
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.min_distance = float('inf')
        self.suggestions = []  # Armazena sugestões de n-grams

class WeightedTrie:
    """
    Classe que representa uma Trie ponderada.
    Fornece métodos para inserir palavras e obter sugestões com base em um prefixo.
    """
    def __init__(self):
        self.root = TrieNode()
        self.ngrams = defaultdict(list)  # Dicionário para armazenar n-grams
    
    def insert(self, word: str):
        """
        Insere uma palavra na Trie.
        Para cada caractere na palavra, atualiza ou adiciona nós filhos conforme necessário.
        Também atualiza a menor distância restante (min_distance) em cada nó.
        """
        node = self.root
        length = len(word)
        for i, char in enumerate(word):
            remaining = length - i
            node.min_distance = min(node.min_distance, remaining)
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.min_distance = 0
    
    def insert_ngram(self, words: list, frequency: int):
        key = " ".join(words).lower()
        key = ''.join(c for c in unicodedata.normalize('NFKD', key) if not unicodedata.combining(c))
        self.ngrams[words[0]].append((key, frequency))
        self.ngrams[words[0]].sort(key=lambda x: -x[1])  # Ordena por frequência decrescente

    
    def _collect_suggestions(self, node, current_prefix, suggestions):
        """
        Método recursivo que coleta todas as palavras a partir de um determinado nó.
        Adiciona cada palavra encontrada à lista de sugestões com seu comprimento.
        """
        if node.is_end:
            suggestions.append((current_prefix, len(current_prefix)))
        for char, child in node.children.items():
            self._collect_suggestions(child, current_prefix + char, suggestions)

    def get_suggestions(self, prefix: str):
        """
        Retorna uma lista de sugestões de palavras que começam com o prefixo fornecido.
        As sugestões são ordenadas pela menor distância e, em caso de empate, em ordem alfabética.
        """
        node = self.root
        prefix_stripped = prefix.strip()
        words = prefix_stripped.split()

        if len(words) == 0: return []

        for char in words[-1]:
            if char not in node.children:
                return  [x[0] for x in self.ngrams.get(words[-1], [])]  # Retorna n-grams associados, se existirem
            node = node.children[char]

        suggestions = []
        self._collect_suggestions(node, prefix, suggestions)
        suggestions.sort(key=lambda x: (len(x[0]) - len(prefix), x[0]))
        
        # Junta palavras da Trie com n-grams associados
        complete = [x[0] for x in suggestions]
        return complete[:5] + [x[0] for x in self.ngrams.get(words[-1], [])]

class AutocompleteDashboard:
    def __init__(self):
        self.trie = WeightedTrie()
        self.load_sample_data()
        self.load_ngrams()
        
        self.window = tk.Tk()
        self.window.title("AutoComplete")
        self.window.geometry("500x400")
        self.window.resizable(True, True)
        
        self.create_widgets()
        self.setup_placeholder()
    
    def load_sample_data(self):
        """
        Carrega palavras de um arquivo de texto e as insere na Trie.
        """
        path = "data/palavras-br.txt"
        with open(path, "r", encoding="utf-8") as arquivo:
            words = [linha.strip() for linha in arquivo if linha.strip()]
        for word in words:
            self.trie.insert(word)
    
    def load_ngrams(self):
        """
        Carrega palavras de um arquivo de texto e as insere na Trie.
        """
        path = "data/n-gram.txt"
        with open(path, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                parts = linha.strip().split()
                if len(parts) < 3:
                    continue
                frequency = int(parts[0])
                words = parts[1:-4]  # Ignoramos a parte final após '||'
                self.trie.insert_ngram(words, frequency)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill='both')

        # Frame para alinhar a Entry e o botão lado a lado
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill='x', expand=True)

        self.entry = ttk.Entry(entry_frame, width=35, font=("Arial", 12))  # Reduzi um pouco a largura
        self.entry.grid(row=0, column=0, sticky="ew")  # Expande horizontalmente
        self.entry.bind("<KeyRelease>", self.update_suggestions)

        # Botão de Clear ao lado da Entry
        self.clear_button = ttk.Button(entry_frame, text="X", width=3, command=self.clear_entry)
        self.clear_button.grid(row=0, column=1, padx=5)  # Adiciona espaço à esquerda

        # Ajusta o layout para expandir corretamente
        entry_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(main_frame, width=40, height=8, font=("Arial", 12))
        self.listbox.pack(fill='both', expand=True)

    def clear_entry(self):
        """Limpa o campo de entrada."""
        self.entry.delete(0, tk.END)
        self.listbox.delete(0, tk.END)

    
    def setup_placeholder(self):
        self.placeholder_text = "Digite para buscar..."
        self.entry.insert(0, self.placeholder_text)
        self.entry.bind("<FocusIn>", self.remove_placeholder)
    
    def remove_placeholder(self, event=None):
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, tk.END)

    def normalize_text(self, text):
        """
        Converte o texto para minúsculas e remove acentos.
        """
        text = text.lower()
        text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
        return text
    
    def update_suggestions(self, event):
        """
        Atualiza a lista de sugestões com base no texto atual do campo de entrada.
        """
        prefix = self.normalize_text(self.entry.get()).strip()
        self.listbox.delete(0, tk.END)
        suggestions = self.trie.get_suggestions(prefix)
        for suggestion in suggestions[:8]:
            self.listbox.insert(tk.END, suggestion)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    dashboard = AutocompleteDashboard()
    dashboard.run()