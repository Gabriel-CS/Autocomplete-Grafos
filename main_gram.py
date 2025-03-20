import tkinter as tk
from tkinter import ttk
import unicodedata
from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.min_distance = float('inf')
        self.suggestions = []  # Armazena sugestões de bigramas e trigramas

class WeightedTrie:
    def __init__(self):
        self.root = TrieNode()
        self.ngrams = defaultdict(list)  # Dicionário para armazenar n-grams
    
    def insert(self, word: str):
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
        key = " ".join(words)
        self.ngrams[words[0]].append((key, frequency))
        self.ngrams[words[0]].sort(key=lambda x: -x[1])  # Ordena por frequência decrescente

    
    def _collect_suggestions(self, node, current_prefix, suggestions):
        if node.is_end:
            suggestions.append((current_prefix, len(current_prefix)))
        for char, child in node.children.items():
            self._collect_suggestions(child, current_prefix + char, suggestions)

    def get_suggestions(self, prefix: str):
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
        #gram = " ".join(words[-2:]) if len(words) >= 2 else words[-1]
        return complete + [x[0] for x in self.ngrams.get(words[-1], [])]

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
        path = "data/palavras-br.txt"
        with open(path, "r", encoding="utf-8") as arquivo:
            words = [linha.strip() for linha in arquivo if linha.strip()]
        for word in words:
            self.trie.insert(word)
    
    def load_ngrams(self):
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
        
        self.entry = ttk.Entry(main_frame, width=40)
        self.entry.pack(fill='x', expand=True)
        self.entry.bind("<KeyRelease>", self.update_suggestions)
        
        self.listbox = tk.Listbox(main_frame, width=40, height=8)
        self.listbox.pack(fill='both', expand=True)
    
    def setup_placeholder(self):
        self.placeholder_text = "Digite para buscar..."
        self.entry.insert(0, self.placeholder_text)
        self.entry.bind("<FocusIn>", self.remove_placeholder)
    
    def remove_placeholder(self, event=None):
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, tk.END)
    
    def update_suggestions(self, event):
        prefix = self.entry.get().strip().lower()
        self.listbox.delete(0, tk.END)
        suggestions = self.trie.get_suggestions(prefix)
        for suggestion in suggestions[:8]:
            self.listbox.insert(tk.END, suggestion)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    dashboard = AutocompleteDashboard()
    dashboard.run()