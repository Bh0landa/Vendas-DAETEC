import tkinter as tk
from tkinter import ttk
from ..core import sales_logic

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

        self.load_products()

    def load_products(self):
        """
        Limpa a tabela e a preenche com os dados atuais do banco de dados.
        """

        for item in self.tree.get_children():
            self.tree.delete(item)

        products_list = sales_logic.get_all_products()

        for i, product in enumerate(products_list):
            id = product[0]
            product_name = product[1]
            product_price = product[2]

            formatted_price = f"R$ {product_price:.2f}".replace('.', ',')
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=(id, product_name, formatted_price), tags=(tag,))

class AddProductDialog(tk.Toplevel):
    """
    Diálogo para adicionar um novo produto.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cadastrar Novo Produto")
        self.geometry("400x200")

        self.transient(parent)
        self.grab_set()

        self.result = None

        # Frame do Formulário
        form_frame = tk.Frame(self, padx=10, pady=10)
        form_frame.pack(fill="both", expand=True)

        # Campo ID do Vendedor
        seller_id_label = tk.Label(form_frame, text="ID do Vendedor:")
        seller_id_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.seller_id_entry = tk.Entry(form_frame)
        self.seller_id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Campo Nome do Produto
        name_label = tk.Label(form_frame, text="Nome do Produto:")
        name_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Campo Preço
        price_label = tk.Label(form_frame, text="Preço (R$):")
        price_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.price_entry = tk.Entry(form_frame)
        self.price_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Botões
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=3, column=1, sticky="e", pady=10)

        ok_button = tk.Button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side="left", padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=self.destroy)
        cancel_button.pack(side="left")

    def _on_ok(self):
        """
        Chamado quando o botão OK é pressionado.
        Valida e armazena os dados e fecha o diálogo.
        """

        seller_id = self.seller_id_entry.get().strip()
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()

        if seller_id and name and price:
            try:
                seller_id_int = int(seller_id)
                price_float = float(price.replace(',', '.'))
                self.result = (name, price_float, seller_id_int)
                self.destroy()
            except ValueError:
                from tkinter import messagebox
                messagebox.showerror("Erro de Entrada", "Por favor, insira um ID e um preço válidos.", parent=self)
        else:
            from tkinter import messagebox
            messagebox.showerror("Erro de Entrada", "Todos os campos são obrigatórios.", parent=self)