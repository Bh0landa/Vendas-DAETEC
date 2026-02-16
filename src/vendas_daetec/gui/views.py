import tkinter as tk
from tkinter import ttk, messagebox

try:
    from ..core import sales_logic

except ImportError:
    # Se falhar, tenta o import para execução direta do arquivo
    import sys
    from pathlib import Path
    # Adiciona o diretório 'src' ao sys.path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from vendas_daetec.core import sales_logic

class ProductsView(tk.Frame):
    """
    Tela de visualização de produtos cadastrados.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._setup_widgets()
        self.load_products()

    def _setup_widgets(self):
        
        # Configurações da tabela de produtos
        
        # Definir colunas
        columns = ("vendedor", "id", "produto", "preco")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        # Estilo
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'))
        self.tree.tag_configure('evenrow', background='#E8E8E8')
        self.tree.tag_configure('oddrow', background='#FFFFFF')

        # Configurar cabeçalhos
        self.tree.heading("vendedor", text="Vendedor")
        self.tree.heading("id", text="ID")
        self.tree.heading("produto", text="Produto")
        self.tree.heading("preco", text="Preço (R$)")

        # Configurar largura das colunas
        
        self.tree.column("vendedor", width=150, anchor=tk.CENTER)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("produto", width=400, anchor=tk.CENTER)
        self.tree.column("preco", width=100, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def load_products(self):
        """
        Carrega os produtos do banco de dados e os exibe na Treeview.
        """

        # Limpa a tabela antes de carregar novos dados
        for item in self.tree.get_children():
            self.tree.delete(item)

        products = sales_logic.get_all_products()

        # Insere os dados na tabela
        for i, product in enumerate(products):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            vendedor, prod_id, prod_nome, prod_preco = product
            
            # Formata o preço para o formato R$ 0,00
            preco_formatado = f"R$ {prod_preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.tree.insert("", tk.END, values=(vendedor, prod_id, prod_nome, preco_formatado), tags=(tag,))

class AddProductDialog(tk.Toplevel):
    """
    Diálogo para adicionar um novo produto.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cadastrar Novo Produto")
        
        # Busca os vendedores antes de construir a janela
        self.vendedores = sales_logic.get_all_sellers()
        if not self.vendedores:
            messagebox.showwarning("Aviso", "Nenhum vendedor cadastrado. Por favor, cadastre um vendedor primeiro.", parent=parent)
            self.destroy() # Fecha a janela se não houver vendedores
            return

        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()
        self.result = None

        form_frame = tk.Frame(self, padx=10, pady=10)
        form_frame.pack(fill="both", expand=True)

        # Campo Vendedor (Combobox)
        seller_label = tk.Label(form_frame, text="Vendedor:")
        seller_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.seller_var = tk.StringVar()
        seller_names = [v[1] for v in self.vendedores] # Extrai apenas os nomes
        self.seller_combo = ttk.Combobox(form_frame, textvariable=self.seller_var, values=seller_names, state="readonly")
        self.seller_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        if seller_names:
            self.seller_combo.current(0)

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

        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=3, column=1, sticky="e", pady=10)

        ok_button = tk.Button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side="left", padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=self.destroy)
        cancel_button.pack(side="left")

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def _on_ok(self):
        seller_name = self.seller_var.get()
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip().replace(',', '.')

        if not seller_name or not name or not price_str:
            messagebox.showerror("Erro de Entrada", "Todos os campos são obrigatórios.", parent=self)
            return

        try:
            price_float = float(price_str)
            if price_float <= 0:
                raise ValueError("O preço deve ser um número positivo.")
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira um preço válido.", parent=self)
            return

        # Encontra o ID do vendedor a partir do nome selecionado
        seller_id = None
        for v_id, v_name in self.vendedores:
            if v_name == seller_name:
                seller_id = v_id
                break
        
        if seller_id is None:
            messagebox.showerror("Erro Interno", "Vendedor selecionado não encontrado.", parent=self)
            return

        self.result = (name, price_float, seller_id)
        self.destroy()

class SaleDialog(tk.Toplevel):
    """
    Janela para registrar uma nova venda (carrinho de compras).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.vendedores = sales_logic.get_all_sellers()
        self.title("Registrar Nova Venda")
        self.geometry("800x600")

        self.transient(parent)
        self.grab_set()

        # Armazena os dados do carrinho e o valor total
        self.cart_items = []
        self.total_venda = 0.0

        # --- Estrutura da Janela ---
        self.selection_frame = ttk.Frame(self, padding="10")
        self.selection_frame.pack(fill="x")

        self.cart_frame = ttk.Frame(self, padding="10")
        self.cart_frame.pack(fill="both", expand=True)

        self.actions_frame = ttk.Frame(self, padding="10")
        self.actions_frame.pack(fill="x")

        # --- Widgets ---
        self._create_selection_widgets()
        self._create_cart_widgets()
        self._create_actions_widgets()


    def _create_selection_widgets(self):
        """Cria os widgets para selecionar vendedor e produto."""
        
        # --- Vendedor ---
        ttk.Label(self.selection_frame, text="Vendedor:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.seller_var = tk.StringVar()
        self.vendedores = sales_logic.get_all_sellers()
        seller_names = [v[1] for v in self.vendedores]

        self.seller_combo = ttk.Combobox(self.selection_frame, textvariable=self.seller_var, values=seller_names, state="readonly", width=25)
        self.seller_combo.grid(row=0, column=1)
        self.seller_combo.bind("<<ComboboxSelected>>", self._on_seller_selected)

        # --- Produto ---
        ttk.Label(self.selection_frame, text="Produto:").grid(row=0, column=2, padx=(10, 5), sticky="w")

        self.product_var = tk.StringVar()
        self.products_cache = [] # Cache para guardar os produtos do vendedor
        self.product_combo = ttk.Combobox(self.selection_frame, textvariable=self.product_var, state="disabled", width=30)
        self.product_combo.grid(row=0, column=3)

        # --- Quantidade ---
        ttk.Label(self.selection_frame, text="Qtd:").grid(row=0, column=4, padx=(10, 5), sticky="w")
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = ttk.Entry(self.selection_frame, textvariable=self.quantity_var, width=5)
        self.quantity_entry.grid(row=0, column=5)

        # --- Botão Adicionar ---
        self.add_item_button = ttk.Button(self.selection_frame, text="Adicionar Item", command=self._add_item_to_cart, state="disabled")
        self.add_item_button.grid(row=0, column=6, padx=(10, 0))


    def _create_cart_widgets(self):
        """Cria a tabela (Treeview) para o carrinho."""
        columns = ("produto", "qtd", "preco_unit", "preco_total")
        self.cart_tree = ttk.Treeview(self.cart_frame, columns=columns, show="headings")

        self.cart_tree.heading("produto", text="Produto")
        self.cart_tree.heading("qtd", text="Qtd.")
        self.cart_tree.heading("preco_unit", text="Preço Unit.")
        self.cart_tree.heading("preco_total", text="Preço Total")

        self.cart_tree.column("qtd", width=60, anchor=tk.CENTER)
        self.cart_tree.column("preco_unit", width=100, anchor=tk.E)
        self.cart_tree.column("preco_total", width=100, anchor=tk.E)

        self.cart_tree.pack(fill="both", expand=True)


    def _create_actions_widgets(self):
        """Cria os widgets no frame de ações (rodapé)."""
        self.total_label = ttk.Label(self.actions_frame, text="Total da Venda: R$ 0,00", font=("Calibri", 12, "bold"))
        self.total_label.pack(side="left")

        self.payment_button = ttk.Button(self.actions_frame, text="Ir para Pagamento", command=self._show_payment_screen, state="disabled")
        self.payment_button.pack(side="right")


    def _on_seller_selected(self, event):
        """Preenche a lista de produtos do vendedor selecionado."""
        selected_name = self.seller_var.get()
        seller_id = [v_id for v_id, v_name in self.vendedores if v_name == selected_name][0]
        
        if seller_id:
            self.product_var.set("") 
            self.products_cache = sales_logic.get_products_by_seller(seller_id)
            product_names = [p[1] for p in self.products_cache]

        if product_names:
            self.product_combo['values'] = product_names
            self.product_combo['state'] = 'readonly'
            self.add_item_button['state'] = 'normal' # Habilita o botão de adicionar
        else:
            messagebox.showinfo("Aviso", "Este vendedor não possui produtos cadastrados.", parent=self)
            self.product_var.set("")
            self.product_combo['values'] = []
            self.product_combo['state'] = 'disabled'
            self.add_item_button['state'] = 'disabled'


    def _add_item_to_cart(self):
        """Adiciona o item selecionado ao carrinho."""
        selected_product_name = self.product_var.get()
        if not selected_product_name:
            messagebox.showwarning("Aviso", "Por favor, selecione um produto.", parent=self)
            return

        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira uma quantidade válida (número inteiro positivo).", parent=self)
            return

        # Encontra os detalhes do produto no cache que já temos
        product_data = None
        for p_id, p_name, p_price in self.products_cache:
            if p_name == selected_product_name:
                product_data = (p_id, p_name, p_price)
                break
        
        if not product_data:
            messagebox.showerror("Erro", "Não foi possível encontrar os detalhes do produto no cache.", parent=self)
            return
        
        product_id, prod_name, unit_price = product_data
        total_price = quantity * unit_price 

        # Adiciona o item ao carrinho visual (Treeview)
        preco_unit_formatado = f"R$ {unit_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        preco_total_formatado = f"R$ {total_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.cart_tree.insert("", tk.END, values=(prod_name, quantity, preco_unit_formatado, preco_total_formatado))

        # Adiciona o item à nossa lista de dados interna
        self.cart_items.append({
            "produto_id": product_id,
            "nome": prod_name,
            "quantidade": quantity,
            "preco_unitario": unit_price,
            "preco_total": total_price
        })

        # Atualiza o valor total da venda
        self.total_venda += total_price
        self.total_label['text'] = f"Total da Venda: R$ {self.total_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Habilita o botão de pagamento
        self.payment_button['state'] = 'normal'

        # Bloqueia a seleção do vendedor
        self.seller_combo['state'] = 'disabled'

        # Limpa os campos para a próxima adição
        self.product_var.set("")
        self.quantity_var.set("1")

    def _show_payment_screen(self):
        """Esconde os frames do carrinho e mostra a tela de pagamento com modos integral e fracionado."""
        # Esconde os frames anteriores
        self.selection_frame.pack_forget()
        self.cart_frame.pack_forget()
        self.actions_frame.pack_forget()

        # Cria o frame principal da tela de pagamento
        self.payment_frame = ttk.Frame(self, padding="10")
        self.payment_frame.pack(fill="both", expand=True)

        # --- Widgets de Controle ---
        control_frame = ttk.Frame(self.payment_frame)
        control_frame.pack(fill="x", pady=(0, 15))

        total_text = f"Total da Venda: R$ {self.total_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ttk.Label(control_frame, text=total_text, font=("Calibri", 14, "bold")).pack(side="left")

        self.integral_payment_var = tk.BooleanVar()
        integral_check = ttk.Checkbutton(control_frame, text="Pagamento Integral", variable=self.integral_payment_var, command=self._toggle_payment_mode)
        integral_check.pack(side="right")

        # --- Frame para Pagamento Integral (escondido inicialmente) ---
        self.integral_mode_frame = ttk.Frame(self.payment_frame)
        # self.integral_mode_frame.pack(fill="x", pady=10) # Não empacotar ainda

        payment_methods = ["Dinheiro", "Pix", "Débito", "Crédito"]
        ttk.Label(self.integral_mode_frame, text="Método de Pagamento:").pack(side="left", padx=(0, 10))
        self.integral_method_var = tk.StringVar()
        self.integral_method_combo = ttk.Combobox(self.integral_mode_frame, textvariable=self.integral_method_var, values=payment_methods, state="readonly")
        self.integral_method_combo.pack(side="left", fill="x", expand=True)
        if payment_methods:
            self.integral_method_combo.current(0)

        # --- Frame para Pagamento Fracionado (visível inicialmente) ---
        self.split_mode_frame = ttk.Frame(self.payment_frame)
        self.split_mode_frame.pack(fill="x", pady=10)

        self.payment_widgets = {}
        for i, method in enumerate(payment_methods):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.split_mode_frame, text=f"{method}: R$", variable=var)
            chk.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            entry = ttk.Entry(self.split_mode_frame, state="disabled")
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            
            chk.config(command=lambda v=var, e=entry: self._toggle_payment_entry(v, e))
            self.payment_widgets[method] = {'var': var, 'entry': entry}

        # --- Botão Finalizar ---
        finish_button = ttk.Button(self.payment_frame, text="Finalizar Venda", command=self._finish_sale)
        finish_button.pack(side="bottom", anchor="e", pady=(20, 0))

    def _toggle_payment_mode(self):
        """Alterna a visibilidade entre os modos de pagamento integral e fracionado."""
        if self.integral_payment_var.get():
            # Modo Integral
            self.split_mode_frame.pack_forget()
            self.integral_mode_frame.pack(fill="x", pady=10)
        else:
            # Modo Fracionado
            self.integral_mode_frame.pack_forget()
            self.split_mode_frame.pack(fill="x", pady=10)

    def _toggle_payment_entry(self, var, entry):
        """Habilita ou desabilita um campo de entrada de pagamento."""
        if var.get():
            entry.config(state="normal")
        else:
            entry.config(state="disabled")

    def _finish_sale(self):
       """Coleta todos os dados e chama a função do backend para registrar a venda."""
       payments = []
       
       # Verifica qual modo de pagamento está ativo
       if self.integral_payment_var.get():
           # Modo de Pagamento Integral
           method = self.integral_method_var.get()
           if not method:
               messagebox.showwarning("Aviso", "Por favor, selecione um método de pagamento.", parent=self)
               return
           payments.append({'metodo': method, 'valor': self.total_venda})
       else:
           # Modo de Pagamento Fracionado
           for method, widgets in self.payment_widgets.items():
               if widgets['var'].get(): # Apenas se o checkbox estiver marcado
                    try:
                        value_str = widgets['entry'].get().replace(',', '.')
                        if not value_str: continue
                        
                        value = float(value_str)
                        if value > 0:
                            payments.append({'metodo': method, 'valor': value})
                    except (ValueError, tk.TclError):
                        messagebox.showerror("Erro de Valor", f"O valor para '{method}' é inválido.", parent=self)
                        return
       
       if not payments:
           messagebox.showwarning("Aviso", "Nenhum pagamento foi inserido.", parent=self)
           return

       # Validação do valor total
       total_pago = sum(p['valor'] for p in payments)
       if not (self.total_venda - 0.01 < total_pago < self.total_venda + 0.01):
            messagebox.showerror("Erro de Valor", 
                                 f"A soma dos pagamentos (R$ {total_pago:.2f}) não corresponde ao total da venda (R$ {self.total_venda:.2f}).",
                                 parent=self)
            return

       # Pega o ID do vendedor
       selected_seller_name = self.seller_var.get()
       vendedor_id = [v_id for v_id, v_name in self.vendedores if v_name == selected_seller_name][0]

       # Chama a função do backend
       success = sales_logic.register_sale(
           vendedor_id=vendedor_id,
           valor_total=self.total_venda,
           cart_items=self.cart_items,
           payments=payments
       )

       if success:
           messagebox.showinfo("Sucesso", "Venda registrada com sucesso!", parent=self)
           self.destroy()
       else:
           messagebox.showerror("Erro no Banco de Dados", 
                                "Ocorreu um erro ao salvar a venda. A transação foi revertida.", 
                                parent=self)