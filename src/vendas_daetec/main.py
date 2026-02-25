from vendas_daetec.gui.app_window import AppWindow
from vendas_daetec.core import sales_logic

def run_app():
    sales_logic.initialize_database()
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    run_app()