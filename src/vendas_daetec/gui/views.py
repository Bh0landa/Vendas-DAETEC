import tkinter as tk
from tkinter import ttk

class ProductsView(tk.Frame):
    """
    Tela de visualização de produtos cadastrados.
    """

    def __init__(self, parent):
        super().__init__(parent)

        # Configurações da tabela de produtos
        
        # Definir colunas
        columns = ("id", "produto", "preco")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        # Estilo
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'))
        self.tree.tag_configure('evenrow', background='#E8E8E8')
        self.tree.tag_configure('oddrow', background='#FFFFFF')

        # Configurar cabeçalhos
        self.tree.heading("id", text="ID")
        self.tree.heading("produto", text="Produto")
        self.tree.heading("preco", text="Preço (R$)")

        # Configurar largura das colunas
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("produto", width=400, anchor=tk.CENTER)
        self.tree.column("preco", width=100, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
