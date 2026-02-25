import tkinter as tk
from tkinter import ttk, messagebox

# Tenta importar a lógica de negócios do módulo core, considerando a estrutura de pacotes
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
        """
        Inicializa a tela de produtos, configurando a tabela e carregando os dados.
        """

        # Inicializa o frame e armazena a referência ao pai
        super().__init__(parent)
        self.parent = parent
        self._setup_widgets()
        self.load_products()

    def _setup_widgets(self):
        """
        Configura os widgets da tela
        """
        
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
        
        # Posicionar os widgets
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configurar o redimensionamento
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def load_products(self):
        """
        Carrega os produtos do banco de dados e os exibe na Treeview.
        """

        # Limpa a tabela antes de carregar novos dados
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Busca os produtos do banco de dados
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
        """
        Inicializa o diálogo, buscando os vendedores para preencher a lista de seleção.
        """
        
        # Inicializa a janela e busca os vendedores antes de construir a interface
        super().__init__(parent)
        self.title("Cadastrar Novo Produto")
        
        # Busca os vendedores antes de construir a janela
        self.vendedores = sales_logic.get_all_sellers()
        
        # Verifica se há vendedores cadastrados antes de permitir o cadastro de produtos
        if not self.vendedores:
            messagebox.showwarning("Aviso", "Nenhum vendedor cadastrado. Por favor, cadastre um vendedor primeiro.", parent=parent)
            self.destroy() # Fecha a janela se não houver vendedores
            return

        # Configurações da janela
        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()
        self.result = None

        # Estrutura da janela
        form_frame = tk.Frame(self, padx=10, pady=10)
        form_frame.pack(fill="both", expand=True)

        # Campo Vendedor
        seller_label = tk.Label(form_frame, text="Vendedor:")
        seller_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Variável para armazenar o vendedor selecionado
        self.seller_var = tk.StringVar()
        seller_names = [v[1] for v in self.vendedores]
        self.seller_combo = ttk.Combobox(form_frame, textvariable=self.seller_var, values=seller_names, state="readonly")
        self.seller_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Define o primeiro vendedor como selecionado por padrão, se houver vendedores disponíveis
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

        # Botões de ação
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=3, column=1, sticky="e", pady=10)

        # Botão de OK
        ok_button = tk.Button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side="left", padx=5)

        # Botão de Cancelar
        cancel_button = tk.Button(button_frame, text="Cancelar", command=self.destroy)
        cancel_button.pack(side="left")

        # Configura o redimensionamento das colunas
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def _on_ok(self):
        """
        Valida os dados de entrada e, se estiverem corretos, armazena o resultado e fecha a janela.
        """

        # Validação dos campos
        seller_name = self.seller_var.get()
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip().replace(',', '.')

        # Verifica se os campos estão preenchidos
        if not seller_name or not name or not price_str:
            messagebox.showerror("Erro de Entrada", "Todos os campos são obrigatórios.", parent=self)
            return

        # Tenta converter o preço para float
        try:
            price_float = float(price_str)
            
            # Verifica se o preço é positivo
            if price_float <= 0:    
                raise ValueError("O preço deve ser um número positivo.")
        
        # Trata erros de conversão e valores inválidos
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira um preço válido.", parent=self)
            return

        # Encontra o ID do vendedor a partir do nome selecionado
        seller_id = None
        
        # Percorre a lista de vendedores e encontra o ID correspondente
        for v_id, v_name in self.vendedores:
            
            # Compara o nome do vendedor na lista com o nome selecionado e encontra o ID correspondente
            if v_name == seller_name:
                seller_id = v_id
                break
        
        # Verifica se o ID do vendedor foi encontrado
        if seller_id is None:
            messagebox.showerror("Erro Interno", "Vendedor selecionado não encontrado.", parent=self)
            return

        # Armazena o resultado como uma tupla e fecha a janela
        self.result = (name, price_float, seller_id)
        self.destroy()

class SaleDialog(tk.Toplevel):
    """
    Janela para registrar uma nova venda (carrinho de compras).
    """
    
    def __init__(self, parent):
        """
        Inicializa a janela de registro de venda, configurando os frames e widgets necessários.
        
        """
        
        # Busca os vendedores antes de construir a janela
        super().__init__(parent)
        self.vendedores = sales_logic.get_all_sellers()
        self.title("Registrar Nova Venda")
        self.geometry("800x600")
        
        # Configura a janela como modal
        self.transient(parent)
        self.grab_set()

        # Armazena os dados do carrinho e o valor total
        self.cart_items = []
        self.total_venda = 0.0

        # Frames principais
        self.selection_frame = ttk.Frame(self, padding="10")
        self.selection_frame.pack(fill="x")

        # Frame para o carrinho
        self.cart_frame = ttk.Frame(self, padding="10")
        self.cart_frame.pack(fill="both", expand=True)

        # Frame para ações
        self.actions_frame = ttk.Frame(self, padding="10")
        self.actions_frame.pack(fill="x")

        # Cria os widgets em cada frame
        self._create_selection_widgets()
        self._create_cart_widgets()
        self._create_actions_widgets()


    def _create_selection_widgets(self):
        """
        Cria os widgets para selecionar vendedor e produto.
        """
        
        # Vendedor
        ttk.Label(self.selection_frame, text="Vendedor:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.seller_var = tk.StringVar()
        self.vendedores = sales_logic.get_all_sellers()
        seller_names = [v[1] for v in self.vendedores]

        # Combobox para seleção de vendedor
        self.seller_combo = ttk.Combobox(self.selection_frame, textvariable=self.seller_var, values=seller_names, state="readonly", width=25)
        self.seller_combo.grid(row=0, column=1)
        self.seller_combo.bind("<<ComboboxSelected>>", self._on_seller_selected)

        # Produto
        ttk.Label(self.selection_frame, text="Produto:").grid(row=0, column=2, padx=(10, 5), sticky="w")
        self.product_var = tk.StringVar()
        self.products_cache = [] # Cache para guardar os produtos do vendedor
        self.product_combo = ttk.Combobox(self.selection_frame, textvariable=self.product_var, state="disabled", width=30)
        self.product_combo.grid(row=0, column=3)

        # Quantidade
        ttk.Label(self.selection_frame, text="Qtd:").grid(row=0, column=4, padx=(10, 5), sticky="w")
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = ttk.Entry(self.selection_frame, textvariable=self.quantity_var, width=5)
        self.quantity_entry.grid(row=0, column=5)

        # Botão para adicionar
        self.add_item_button = ttk.Button(self.selection_frame, text="Adicionar Item", command=self._add_item_to_cart, state="disabled")
        self.add_item_button.grid(row=0, column=6, padx=(10, 0))


    def _create_cart_widgets(self):
        """
        Cria a tabela (Treeview) para o carrinho.
        """
        
        # Define as colunas para o carrinho
        columns = ("produto", "qtd", "preco_unit", "preco_total")
        self.cart_tree = ttk.Treeview(self.cart_frame, columns=columns, show="headings")

        # Cabeçalhos
        self.cart_tree.heading("produto", text="Produto")
        self.cart_tree.heading("qtd", text="Qtd.")
        self.cart_tree.heading("preco_unit", text="Preço Unit.")
        self.cart_tree.heading("preco_total", text="Preço Total")

        # Colunas
        self.cart_tree.column("qtd", width=60, anchor=tk.CENTER)
        self.cart_tree.column("preco_unit", width=100, anchor=tk.E)
        self.cart_tree.column("preco_total", width=100, anchor=tk.E)

        # Ajuste do tamanho da tabela
        self.cart_tree.pack(fill="both", expand=True)


    def _create_actions_widgets(self):
        """
        Cria os widgets no frame de ações (rodapé).
        """
        
        # Label para mostrar o total da venda
        self.total_label = ttk.Label(self.actions_frame, text="Total da Venda: R$ 0,00", font=("Calibri", 12, "bold"))
        self.total_label.pack(side="left")

        # Botão para ir para a tela de pagamento
        self.payment_button = ttk.Button(self.actions_frame, text="Ir para Pagamento", command=self._show_payment_screen, state="disabled")
        self.payment_button.pack(side="right")


    def _on_seller_selected(self, event):
        """
        Preenche a lista de produtos do vendedor selecionado.
        """

        # Obtém o ID do vendedor selecionado
        selected_name = self.seller_var.get()
        seller_id = [v_id for v_id, v_name in self.vendedores if v_name == selected_name][0]
        
        # Busca os produtos do vendedor selecionado e atualiza a combobox de produtos
        if seller_id:
            self.product_var.set("") 
            self.products_cache = sales_logic.get_products_by_seller(seller_id)
            product_names = [p[1] for p in self.products_cache]

        # Atualiza a combobox de produtos e o estado do botão de adicionar
        if product_names:
            self.product_combo['values'] = product_names
            self.product_combo['state'] = 'readonly'
            self.add_item_button['state'] = 'normal'
        
        # Se o vendedor não tiver produtos, desabilita a seleção de produto e o botão de adicionar
        else:
            messagebox.showinfo("Aviso", "Este vendedor não possui produtos cadastrados.", parent=self)
            self.product_var.set("")
            self.product_combo['values'] = []
            self.product_combo['state'] = 'disabled'
            self.add_item_button['state'] = 'disabled'


    def _add_item_to_cart(self):
        """
        Adiciona o item selecionado ao carrinho.
        """
        
        # Obtém os dados do produto selecionado
        selected_product_name = self.product_var.get()
        
        # Valida a seleção do produto e a quantidade
        if not selected_product_name:
            messagebox.showwarning("Aviso", "Por favor, selecione um produto.", parent=self)
            return

        # Valida a quantidade, garantindo que seja um número inteiro positivo
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError
        
        # Trata erros de conversão e valores inválidos
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira uma quantidade válida (número inteiro positivo).", parent=self)
            return

        # Encontra os detalhes do produto no cache que já temos
        product_data = None
        
        # Percorre o cache de produtos para encontrar os detalhes do produto selecionado
        for p_id, p_name, p_price in self.products_cache:
            
            # Compara o nome do produto na lista com o nome selecionado e encontra os detalhes correspondentes
            if p_name == selected_product_name:
                product_data = (p_id, p_name, p_price)
                break
        
        # Verifica se os detalhes do produto foram encontrados no cache
        if not product_data:
            messagebox.showerror("Erro", "Não foi possível encontrar os detalhes do produto no cache.", parent=self)
            return
        
        # Calcula o preço total do item
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
        """
        Esconde os frames do carrinho e mostra a tela de pagamento com modos integral e fracionado.
        """
        
        # Esconde os frames anteriores
        self.selection_frame.pack_forget()
        self.cart_frame.pack_forget()
        self.actions_frame.pack_forget()

        # Cria o frame principal da tela de pagamento
        self.payment_frame = ttk.Frame(self, padding="10")
        self.payment_frame.pack(fill="both", expand=True)

        # Widget de controle
        control_frame = ttk.Frame(self.payment_frame)
        control_frame.pack(fill="x", pady=(0, 15))

        # Label do total da venda
        total_text = f"Total da Venda: R$ {self.total_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ttk.Label(control_frame, text=total_text, font=("Calibri", 14, "bold")).pack(side="left")

        # Checkbox para escolher entre pagamento integral ou fracionado
        self.integral_payment_var = tk.BooleanVar(1)
        integral_check = ttk.Checkbutton(control_frame, text="Pagamento Integral", variable=self.integral_payment_var, command=self._toggle_payment_mode)
        integral_check.pack(side="right")

        # Frame para Pagamento Integral
        self.integral_mode_frame = ttk.Frame(self.payment_frame)

        # Opções de método de pagamento para o modo integral
        payment_methods = ["Dinheiro", "Pix", "Débito", "Crédito"]
        ttk.Label(self.integral_mode_frame, text="Método de Pagamento:").pack(side="left", padx=(0, 10))
        self.integral_method_var = tk.StringVar()
        self.integral_method_combo = ttk.Combobox(self.integral_mode_frame, textvariable=self.integral_method_var, values=payment_methods, state="readonly")
        self.integral_method_combo.pack(side="left", fill="x", expand=True)
        
        # Define o primeiro método de pagamento como selecionado por padrão, se houver métodos disponíveis
        if payment_methods:
            self.integral_method_combo.current(0)

        # Frame para Pagamento Fracionado
        self.split_mode_frame = ttk.Frame(self.payment_frame)
        self.split_mode_frame.pack(fill="x", pady=10)

        # Dicionário para armazenar os widgets de pagamento fracionado
        self.payment_widgets = {}
        
        # Cria os checkboxes e campos de entrada para cada método de pagamento no modo fracionado
        for i, method in enumerate(payment_methods):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.split_mode_frame, text=f"{method}: R$", variable=var)
            chk.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Campo de entrada para o valor do pagamento
            entry = ttk.Entry(self.split_mode_frame, state="disabled")
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            
            # Configura o comando do checkbox para habilitar/desabilitar o campo de entrada correspondente
            chk.config(command=lambda v=var, e=entry: self._toggle_payment_entry(v, e))
            self.payment_widgets[method] = {'var': var, 'entry': entry}

        # Botão para finalizar a venda
        finish_button = ttk.Button(self.payment_frame, text="Finalizar Venda", command=self._finish_sale)
        finish_button.pack(side="bottom", anchor="e", pady=(20, 0))

    def _toggle_payment_mode(self):
        """
        Alterna a visibilidade entre os modos de pagamento integral e fracionado.
        """

        # Verifica o estado do checkbox de pagamento integral
        if self.integral_payment_var.get():
            
            # Modo Integral
            self.split_mode_frame.pack_forget()
            self.integral_mode_frame.pack(fill="x", pady=10)
        
        # Se o pagamento integral não estiver selecionado, mostra o modo fracionado
        else:
           
            # Modo Fracionado
            self.integral_mode_frame.pack_forget()
            self.split_mode_frame.pack(fill="x", pady=10)

    def _toggle_payment_entry(self, var, entry):
        """
        Habilita ou desabilita um campo de entrada de pagamento.
        """
        
        # Verifica o estado do checkbox e habilita ou desabilita o campo de entrada correspondente
        if var.get():
            entry.config(state="normal")
        
        # Se o checkbox for desmarcado, limpa o campo de entrada e o desabilita
        else:
            entry.config(state="disabled")

    def _finish_sale(self):
        """
        Coleta todos os dados e chama a função do backend para registrar a venda.
        """
       
        # Lista para armazenar os métodos de pagamento e seus valores
        payments = []
       
        # Verifica qual modo de pagamento está ativo
        if self.integral_payment_var.get():
            
            # Modo de Pagamento Integral
            method = self.integral_method_var.get()
           
            # Valida se um método de pagamento foi selecionado
            if not method:
                messagebox.showwarning("Aviso", "Por favor, selecione um método de pagamento.", parent=self)
                return
           
            # Para o pagamento integral, o valor é o total da venda
            payments.append({'metodo': method, 'valor': self.total_venda})
       
        # Se o pagamento integral não estiver selecionado, coleta os valores do modo fracionado
        else:
            
            # Modo de Pagamento Fracionado
            for method, widgets in self.payment_widgets.items():
               
                # Verifica se o método de pagamento foi selecionado
                if widgets['var'].get():
                    
                    # Tenta converter o valor inserido para float, tratando erros de entrada
                    try:
                        value_str = widgets['entry'].get().replace(',', '.')
                        
                        # Se o campo estiver vazio, ignora este método de pagamento
                        if not value_str: continue
                        
                        # Tenta converter o valor para float
                        value = float(value_str)
                        
                        # Considera apenas valores positivos para o pagamento
                        if value > 0:
                            payments.append({'metodo': method, 'valor': value})
                    
                    # Trata erros de conversão e valores inválidos, mostrando uma mensagem de erro para o usuário
                    except (ValueError, tk.TclError):
                        messagebox.showerror("Erro de Valor", f"O valor para '{method}' é inválido.", parent=self)
                        return
       
        # Valida se pelo menos um método de pagamento foi inserido
        if not payments:
            messagebox.showwarning("Aviso", "Nenhum pagamento foi inserido.", parent=self)
            return

        # Validação do valor total
        total_pago = sum(p['valor'] for p in payments)
       
        # Verifica se a soma dos pagamentos corresponde ao total da venda
        if not (self.total_venda - 0.01 < total_pago < self.total_venda + 0.01):
            messagebox.showerror("Erro de Valor", f"A soma dos pagamentos (R$ {total_pago:.2f}) não corresponde ao total da venda (R$ {self.total_venda:.2f}).", parent=self)
            return

        # Pega o ID do vendedor
        selected_seller_name = self.seller_var.get()
        vendedor_id = [v_id for v_id, v_name in self.vendedores if v_name == selected_seller_name][0]

        # Chama a função do backend
        success = sales_logic.register_sale(vendedor_id=vendedor_id, valor_total=self.total_venda, cart_items=self.cart_items, payments=payments)

        if success:
            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!", parent=self)
            self.destroy()

        else:
            messagebox.showerror("Erro no Banco de Dados", "Ocorreu um erro ao salvar a venda. A transação foi revertida.", parent=self)