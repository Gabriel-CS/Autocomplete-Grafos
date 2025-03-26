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
        return complete[:10] + [x[0] for x in self.ngrams.get(words[-1], [])]