import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from .views import ProductsView, AddProductDialog, SaleDialog
from ..core import sales_logic

class AppWindow(tk.Tk):
    """
    Janela principal da aplicação de vendas DAETEC.
    """
    
    def __init__(self):
        """
        Inicializa a janela principal, configura o layout e os componentes.
        """
        
        # Chama o construtor da classe pai
        super().__init__()
        
        # Janela principal
        self.title("Vendas DAETEC")
        self.geometry("1024x768")
        self.state("zoomed")

        # Menu de navegação
        self.menu_frame = tk.Frame(self, bg="#f0f0f0", height=40)
        self.menu_frame.pack(side="top", fill="x")
        self.menu_frame.pack_propagate(False)

        # Frame principal
        self.main_content_frame = tk.Frame(self)
        self.main_content_frame.pack(side="top", fill="both", expand=True)

        # Configuração do Frame de conteúdo principal
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        # Botões do menu
        self._setup_navigation()

        self.frames = {}

        # Instancia das telas utilizadas
        self.products_view_frame = ProductsView(self.main_content_frame)
        self.frames[ProductsView] = self.products_view_frame

        # Coloca a tela de produtos no grid
        self.products_view_frame.grid(row=0, column=0, sticky="nsew")

        # Mostra a tela inicial
        self.show_frame(ProductsView)

    def show_frame(self, frame_class):
        """
        Mostra uma tela especificada e esconde as outras.
        """
        
        # Alterna a visibilidade dos frames para mostrar apenas o frame solicitado
        frame = self.frames[frame_class]
        frame.tkraise()

    def _setup_navigation(self):
        """
        Cria os botões de navegação no menu.
        """
        
        # Botão de cadastrar produto
        add_product_button = tk.Button(self.menu_frame, text="Cadastrar Produto", command=self._add_product_dialog)
        add_product_button.pack(side="left", padx=(10, 0), pady=5)

        # Botão de descadastrar produto
        delete_product_button = tk.Button(self.menu_frame, text="Descadastrar Produto", command=self._delete_product_dialog)
        delete_product_button.pack(side="left", padx=0, pady=5)

        # Botão de Cadastrar vendedor
        add_seller_button = tk.Button(self.menu_frame, text="Cadastrar Vendedor", command=self._open_add_seller_dialog)
        add_seller_button.pack(side="left", padx=0, pady=5)

        # Botão de descadastrar vendedor
        delete_seller_button = tk.Button(self.menu_frame, text="Descadastrar Vendedor", command=self._open_delete_seller_dialog)
        delete_seller_button.pack(side="left", padx=0, pady=5)

        # Botão mostrar vendedores
        show_sellers_button = tk.Button(self.menu_frame, text="Mostrar Vendedores", command=self._show_sellers_window)
        show_sellers_button.pack(side="left", padx=0, pady=5)

        # Botão de relatório
        report_button = tk.Button(self.menu_frame, text="Gerar Relatório", command=self._generate_report)
        report_button.pack(side="left", padx=0, pady=5)

        # Botão de limpar histórico
        clear_history_button = tk.Button(self.menu_frame, text="Limpar Histórico", command=self._clear_history)
        clear_history_button.pack(side="left", padx=0, pady=5)

        # Botão de Vender
        sell_button = tk.Button(self.menu_frame, text="Vender", command=self._open_sale_dialog)
        sell_button.pack(side="right", padx=(0, 10), pady=5)

    def _show_sellers_window(self):
        """
        Abre uma nova janela para mostrar a lista de vendedores.
        """

        # Janela para exibir os vendedores
        sellers_win = tk.Toplevel(self)
        sellers_win.title("Lista de Vendedores")
        sellers_win.geometry("400x300")

        # Deixa a janela modal
        sellers_win.transient(self)
        sellers_win.grab_set()

        # Frame para a tabela de vendedores
        table_frame = tk.Frame(sellers_win)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configuração da tabela de vendedores
        columns = ("id", "nome")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        tree.heading("id", text="ID")
        tree.heading("nome", text="Nome do Vendedor")
        tree.column("id", width=80, anchor=tk.CENTER)
        tree.column("nome", width=280)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        # Frame para o botão
        button_frame = tk.Frame(sellers_win)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        back_button = tk.Button(button_frame, text="Voltar", command=sellers_win.destroy)
        back_button.pack()
        sellers_list = sales_logic.get_all_sellers()
        
        # Popula a tabela com os vendedores
        for seller in sellers_list:
            tree.insert("", tk.END, values=seller)

    def _open_add_seller_dialog(self):
        """
        Abre um diálogo para adicionar um novo vendedor.
        """

        # Solicita o nome do vendedor ao usuário
        name = simpledialog.askstring("Cadastrar Vendedor", "Digite o nome do vendedor:", parent=self)
        
        # Verifica se o usuário inseriu um nome
        if name:
            
            if sales_logic.add_seller(name):
                messagebox.showinfo("Sucesso", f"Vendedor '{name}' cadastrado com sucesso!")
            
            else:
                messagebox.showerror("Erro", f"Não foi possível cadastrar o vendedor '{name}'.\nVerifique se ele já não está na lista.")
    
    def _open_delete_seller_dialog(self):
        """
        Abre um diálogo para deletar um vendedor existente.
        """
        
        # Solicita o ID do vendedor a ser deletado
        seller_id = simpledialog.askinteger("Descadastrar Vendedor", "Digite o ID do vendedor a ser removido:", parent=self)
        
        # Verifica se o usuário inseriu um ID
        if seller_id:
            result = sales_logic.delete_seller(seller_id)
            
            # Exibe uma mensagem com base no resultado da operação
            if result is True:
                messagebox.showinfo("Sucesso", f"Vendedor com ID {seller_id} deletado com sucesso!")
            
            # Se a exclusão falhou devido a restrições de integridade (vendedor associado a produtos ou vendas), informa o usuário
            elif result == "constraint_failed":
                messagebox.showerror("Operação Bloqueada", f"Não é possível remover o vendedor com ID {seller_id} porque ele possui produtos ou vendas associadas a ele.")
            
            # Se o vendedor não for encontrado, informa o usuário
            elif result == "not_found":
                messagebox.showwarning("Aviso", f"Nenhum vendedor encontrado com o ID {seller_id}.")
            
            # Para qualquer outro resultado inesperado, mostra uma mensagem de erro genérica
            else:
                messagebox.showerror("Erro", f"Ocorreu um erro desconhecido ao tentar deletar o vendedor com ID {seller_id}.")

    def _add_product_dialog(self):
        """
        Abre o diálogo para adicionar um novo produto.
        """

        # Janela de cadastro de produto
        dialog = AddProductDialog(self)

        # Verifica se o resultado é válido e tenta adicionar o produto
        if dialog.result:
            name, price, seller_id = dialog.result
            
            if sales_logic.add_product(name, price, seller_id):
                messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")

                # Atualiza a visualização da tabela de produtos
                self.products_view_frame.load_products()
            
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao adicionar o produto.")
        
        else:
            print("Cadastro de produto cancelado.")
    
    def _delete_product_dialog(self):
        """
        Abre um diálogo para deletar um produto existente.
        """
        
        # Solicita o ID do produto a ser deletado
        product_id = simpledialog.askstring("Descadastrar Produto", "Digite o ID do produto a ser removido (ex: PROD-0001):", parent=self)
        
        # Verifica se o usuário inseriu um ID
        if product_id:

            # Normaliza o ID do produto
            product_id = product_id.strip().upper()
            
            # Tenta deletar o produto usando a lógica de negócios
            if sales_logic.delete_product(product_id):
                messagebox.showinfo("Sucesso", f"Produto com ID {product_id} deletado com sucesso!")
                
                self.products_view_frame.load_products()
            
            else:
                messagebox.showerror("Erro", f"Não foi possível deletar o produto com ID {product_id}.\nVerifique se o ID está correto.")

    def _open_sale_dialog(self):
        """
        Abre o diálogo para registrar uma nova venda.
        """
        
        # Abre a janela de registro de venda
        SaleDialog(self)

    def _generate_report(self):
        """
        Gera o relatório de vendas e pede ao usuário para salvar em um arquivo.
        """
        
        # Gera o conteúdo do relatório usando a lógica de negócios
        report_content = sales_logic.generate_sales_report()

        # Pede ao usuário para escolher onde salvar o arquivo
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], title="Salvar Relatório de Vendas")

        # Verifica se o usuário selecionou um caminho para salvar o arquivo
        if not file_path:
            return

        # Tenta salvar o relatório no arquivo escolhido
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(report_content)
            
            messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso em:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo.\nErro: {e}")
    
    def _clear_history(self):
        """
        Limpa o histórico de vendas após confirmação.
        """

        # Solicita confirmação do usuário antes de limpar o histórico
        confirm = messagebox.askyesno(
            "Confirmar Limpeza",
            "Tem certeza que deseja apagar TODO o histórico de vendas?\n\n"
            "Isso removerá irreversivelmente todas as vendas registradas,\n"
            "mas manterá os cadastros de Vendedores e Produtos.\n\n"
            "Recomendamos que gere um relatório antes de prosseguir.",
            parent=self,
            icon='warning'
        )

        # Se o usuário confirmar, chama a função de lógica de negócios para limpar os dados de vendas
        if confirm:
            success = sales_logic.clear_sales_data()
            
            if success:
                messagebox.showinfo("Sucesso", "Histórico de vendas apagado com sucesso!", parent=self)
            
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao tentar limpar o histórico.", parent=self)