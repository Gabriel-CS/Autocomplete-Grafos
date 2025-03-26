import tkinter as tk
from tkinter import ttk
import unicodedata
from trie import WeightedTrie

class AutocompleteDashboard:
    def __init__(self):
        self.trie = WeightedTrie()
        self.load_sample_data()
        self.load_ngrams()
        
        self.window = tk.Tk()
        self.window.title("AutoComplete")
        self.window.geometry("600x600")
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
                words = parts[1:-4]
                self.trie.insert_ngram(words, frequency)
        
    def create_widgets(self):
        """
        Cria os widgets principais da interface gráfica.
        """
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill='both')

        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill='x', expand=True)

        self.entry = ttk.Entry(entry_frame, width=35, font=("Arial", 16))
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<KeyRelease>", self.update_suggestions)

        style = ttk.Style()
        style.configure("Clear.TButton", font=("Arial", 12), padding=(2, 2))

        self.clear_button = ttk.Button(entry_frame, text="X", width=3, command=self.clear_entry, style="Clear.TButton")
        self.clear_button.grid(row=0, column=1, padx=5)

        entry_frame.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(main_frame, width=40, height=15, font=("Arial", 16))
        self.listbox.pack(fill='both', expand=True)


    def clear_entry(self):
        """
        Limpa o campo de entrada e a lista de sugestões.
        """
        self.entry.delete(0, tk.END)
        self.listbox.delete(0, tk.END)

    
    def setup_placeholder(self):
        """
        Configura o texto de placeholder no campo de entrada.
        """
        self.placeholder_text = "Digite para buscar..."
        self.entry.insert(0, self.placeholder_text)
        self.entry.bind("<FocusIn>", self.remove_placeholder)
    
    def remove_placeholder(self, event=None):
        """
        Remove o texto de placeholder quando o campo de entrada é focado.
        """
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
        for suggestion in suggestions[:20]:
            self.listbox.insert(tk.END, suggestion)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    dashboard = AutocompleteDashboard()
    dashboard.run()