import tkinter as tk
import mysql.connector
from tkinter import messagebox
from tkinter import ttk


def mostrar_frame(frame):
    frame.tkraise()

def salvar_autor():
    nome = entry_nome.get()
    
    if nome:
        try:
            conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                port=3306,
                database="biblioteca"
            )
            cursor = conexao.cursor()
            sql = "INSERT INTO autor (nome) VALUES (%s)"
            valores = (nome,)
            cursor.execute(sql, valores)
            conexao.commit()

            label_status_autor.config(text=f'Dados do autor "{nome}" salvos com sucesso!', fg="green")
            entry_nome.delete(0, tk.END)

        except mysql.connector.Error as erro:
            messagebox.showerror("Erro de conexão", f"Erro ao conectar ao banco:\n{erro}")
        finally:
            cursor.close()
            conexao.close()
    else:
        label_status_autor.config(text="Por favor, digite o nome do autor.", fg="red")

def salvar_livro():
    titulo = entry_titulo.get()
    autor_id = entry_autorid.get()

    if titulo and autor_id:
        try:
            conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                port=3306,
                database="biblioteca"
            )
            cursor = conexao.cursor()
            sql = "INSERT INTO livro (titulo, autor_id) VALUES (%s, %s)"
            valores = (titulo, autor_id)
            cursor.execute(sql, valores)
            conexao.commit()

            label_status_livro.config(text=f'Dados do livro "{titulo}" salvos com sucesso!', fg="green")
            entry_titulo.delete(0, tk.END)
            entry_autorid.delete(0, tk.END)

        except mysql.connector.Error as erro:
            messagebox.showerror("Erro de conexão", f"Erro ao conectar ao banco:\n{erro}")
        finally:
            cursor.close()
            conexao.close()
    else:
        label_status_livro.config(text="Por favor, preencha todos os campos.", fg="red")

def carregar_autores():
    for i in tree_autores.get_children():
        tree_autores.delete(i)
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3306,
            database="biblioteca"
        )
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome FROM autor")
        for id_autor, nome in cursor.fetchall():
            tree_autores.insert("", "end", values=(id_autor, nome))
        cursor.close()
        conexao.close()
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro de conexão", f"Erro ao carregar autores:\n{erro}")

def carregar_livros():
    for i in tree_livros.get_children():
        tree_livros.delete(i)
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3306,
            database="biblioteca"
        )
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT livro.id, livro.titulo, autor.nome 
            FROM livro 
            JOIN autor ON livro.autor_id = autor.id
        """)
        for id_livro, titulo, nome_autor in cursor.fetchall():
            tree_livros.insert("", "end", values=(id_livro, titulo, nome_autor))
        cursor.close()
        conexao.close()
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro de conexão", f"Erro ao carregar livros:\n{erro}")

# --- NOVAS FUNÇÕES PARA EDITAR E APAGAR ---

def editar_autor():
    item_selecionado = tree_autores.focus()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um autor para editar.")
        return

    autor_id, nome_atual = tree_autores.item(item_selecionado, "values")

    def salvar_edicao():
        novo_nome = entry_edit_nome.get()
        if not novo_nome:
            messagebox.showwarning("Aviso", "Nome não pode ficar vazio.")
            return
        try:
            conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                port=3306,
                database="biblioteca"
            )
            cursor = conexao.cursor()
            sql = "UPDATE autor SET nome = %s WHERE id = %s"
            cursor.execute(sql, (novo_nome, autor_id))
            conexao.commit()
            cursor.close()
            conexao.close()

            carregar_autores()
            popup.destroy()
            messagebox.showinfo("Sucesso", "Autor atualizado com sucesso!")
        except mysql.connector.Error as erro:
            messagebox.showerror("Erro", f"Erro ao atualizar autor:\n{erro}")

    popup = tk.Toplevel()
    popup.title("Editar Autor")
    popup.geometry("300x150")
    tk.Label(popup, text="Novo nome:").pack(pady=5)
    entry_edit_nome = tk.Entry(popup, width=30)
    entry_edit_nome.insert(0, nome_atual)
    entry_edit_nome.pack(pady=5)
    tk.Button(popup, text="Salvar", command=salvar_edicao).pack(pady=10)

def apagar_autor():
    item_selecionado = tree_autores.focus()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um autor para apagar.")
        return
    autor_id, nome = tree_autores.item(item_selecionado, "values")

    confirmar = messagebox.askyesno("Confirmar", f"Tem certeza que deseja apagar o autor '{nome}'?\nIsso também pode apagar livros relacionados!")
    if confirmar:
        try:
            conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                port=3306,
                database="biblioteca"
            )
            cursor = conexao.cursor()
            # Opcional: apagar livros relacionados antes, se sua FK não faz isso automaticamente
            cursor.execute("DELETE FROM livro WHERE autor_id = %s", (autor_id,))
            cursor.execute("DELETE FROM autor WHERE id = %s", (autor_id,))
            conexao.commit()
            cursor.close()
            conexao.close()
            carregar_autores()
            carregar_livros()  # Atualiza lista de livros também
            messagebox.showinfo("Sucesso", f"Autor '{nome}' apagado com sucesso!")
        except mysql.connector.Error as erro:
            messagebox.showerror("Erro", f"Erro ao apagar autor:\n{erro}")

def editar_livro():
    item_selecionado = tree_livros.focus()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um livro para editar.")
        return

    livro_id, titulo_atual, autor_nome_atual = tree_livros.item(item_selecionado, "values")

    def salvar_edicao():
        novo_titulo = entry_edit_titulo.get()
        novo_autor_id = entry_edit_autorid.get()
        if not novo_titulo or not novo_autor_id:
            messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos.")
            return
        try:
            conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                port=3306,
                database="biblioteca"
            )
            cursor = conexao.cursor()
            sql = "UPDATE livro SET titulo = %s, autor_id = %s WHERE id = %s"
            cursor.execute(sql, (novo_titulo, novo_autor_id, livro_id))
            conexao.commit()
            cursor.close()
            conexao.close()

            carregar_livros()
            popup.destroy()
            messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")
        except mysql.connector.Error as erro:
            messagebox.showerror("Erro", f"Erro ao atualizar livro:\n{erro}")

    popup = tk.Toplevel()
    popup.title("Editar Livro")
    popup.geometry("300x200")

    tk.Label(popup, text="Novo título:").pack(pady=5)
    entry_edit_titulo = tk.Entry(popup, width=30)
    entry_edit_titulo.insert(0, titulo_atual)
    entry_edit_titulo.pack(pady=5)

    tk.Label(popup, text="Novo ID do autor:").pack(pady=5)
    entry_edit_autorid = tk.Entry(popup, width=30)
    entry_edit_autorid.insert(0, "")
    # Opcional: pegar o id do autor pelo nome atual
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3306,
            database="biblioteca"
        )
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM autor WHERE nome = %s", (autor_nome_atual,))
        resultado = cursor.fetchone()
        if resultado:
            entry_edit_autorid.insert(0, resultado[0])
        cursor.close()
        conexao.close()
    except:
        pass
    entry_edit_autorid.pack(pady=5)

    tk.Button(popup, text="Salvar", command=salvar_edicao).pack(pady=10)

def apagar_livro():
    item_selecionado = tree_livros.focus()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um livro para apagar.")
        return
    livro_id, titulo, autor_nome = tree_livros.item(item_selecionado, "values")

    confirmar = messagebox.askyesno("Confirmar", f"Tem certeza que deseja apagar o livro '{titulo}'?")
    if confirmar:
        try:
            conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                port=3306,
                database="biblioteca"
            )
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM livro WHERE id = %s", (livro_id,))
            conexao.commit()
            cursor.close()
            conexao.close()
            carregar_livros()
            messagebox.showinfo("Sucesso", f"Livro '{titulo}' apagado com sucesso!")
        except mysql.connector.Error as erro:
            messagebox.showerror("Erro", f"Erro ao apagar livro:\n{erro}")

def sobre():
    popup = tk.Toplevel()
    popup.title("Sobre")
    popup.geometry("300x200")
    
    
    texto_sobre = (
        "Sistema de biblioteca com tabelas autor e livro" 
    )
    
    label_sobre = tk.Label(popup, text=texto_sobre, justify="left", padx=10, pady=10)
    label_sobre.pack()
    
root = tk.Tk()
root.title("Biblioteca")

container = ttk.Frame(root)
container.pack(fill='both', expand=True)

frame1 = ttk.Frame(container)  # Salvar autor
frame2 = ttk.Frame(container)  # Lista de autores
frame3 = ttk.Frame(container)  # Salvar livro
frame4 = ttk.Frame(container)  # Lista de livros

for frame in (frame1, frame2, frame3, frame4):
    frame.grid(row=0, column=0, sticky='nsew')

# Frame 1 - Salvar Autor
ttk.Label(frame1, text="Salvar Autor", font=("Arial", 16)).pack(pady=10)

label_nome = tk.Label(frame1, text="Digite o nome do autor")
label_nome.pack(pady=5)
entry_nome = tk.Entry(frame1, width=40)
entry_nome.pack(pady=5)

botao_salvar_autor = tk.Button(frame1, text="Salvar", command=salvar_autor)
botao_salvar_autor.pack(pady=10)

label_status_autor = tk.Label(frame1, text="")
label_status_autor.pack(pady=5)

# Frame 2 - Lista de Autores
ttk.Label(frame2, text="Lista de Autores", font=("Arial", 16)).pack(pady=10)

colunas_autores = ("ID", "Nome")
tree_autores = ttk.Treeview(frame2, columns=colunas_autores, show='headings')
tree_autores.heading("ID", text="ID")
tree_autores.heading("Nome", text="Nome")
tree_autores.pack(fill='both', expand=True, pady=10)

btn_frame_autores = tk.Frame(frame2)
btn_frame_autores.pack()

btn_editar_autor = tk.Button(btn_frame_autores, text="Editar", command=editar_autor)
btn_editar_autor.grid(row=0, column=0, padx=5)

btn_apagar_autor = tk.Button(btn_frame_autores, text="Apagar", command=apagar_autor)
btn_apagar_autor.grid(row=0, column=1, padx=5)

# Frame 3 - Salvar Livro
ttk.Label(frame3, text="Salvar Livro", font=("Arial", 16)).pack(pady=10)

label_titulo = tk.Label(frame3, text="Digite o título do livro")
label_titulo.pack(pady=5)
entry_titulo = tk.Entry(frame3, width=40)
entry_titulo.pack(pady=5)

label_autorid = tk.Label(frame3, text="Digite o ID do autor")
label_autorid.pack(pady=5)
entry_autorid = tk.Entry(frame3, width=40)
entry_autorid.pack(pady=5)

botao_salvar_livro = tk.Button(frame3, text="Salvar", command=salvar_livro)
botao_salvar_livro.pack(pady=10)

label_status_livro = tk.Label(frame3, text="")
label_status_livro.pack(pady=5)

# Frame 4 - Lista de Livros
ttk.Label(frame4, text="Lista de Livros", font=("Arial", 16)).pack(pady=10)

colunas_livros = ("ID", "Título", "Autor")
tree_livros = ttk.Treeview(frame4, columns=colunas_livros, show='headings')
tree_livros.heading("ID", text="ID")
tree_livros.heading("Título", text="Título")
tree_livros.heading("Autor", text="Autor")
tree_livros.pack(fill='both', expand=True, pady=10)

btn_frame_livros = tk.Frame(frame4)
btn_frame_livros.pack()

btn_editar_livro = tk.Button(btn_frame_livros, text="Editar", command=editar_livro)
btn_editar_livro.grid(row=0, column=0, padx=5)

btn_apagar_livro = tk.Button(btn_frame_livros, text="Apagar", command=apagar_livro)
btn_apagar_livro.grid(row=0, column=1, padx=5)

# Menus
menubar = tk.Menu(root)

# Menu Autores
autores_menu = tk.Menu(menubar, tearoff=0)
autores_menu.add_command(label="Salvar autor", command=lambda: mostrar_frame(frame1))
autores_menu.add_command(label="Lista de Autores", command=lambda: [mostrar_frame(frame2), carregar_autores()])
menubar.add_cascade(label="Autores", menu=autores_menu)

# Menu de Livros 
livros_menu = tk.Menu(menubar, tearoff=0)
livros_menu.add_command(label="Salvar Livro", command=lambda: mostrar_frame(frame3))
livros_menu.add_command(label="Lista de Livros", command=lambda: [mostrar_frame(frame4), carregar_livros()])
menubar.add_cascade(label="Livros", menu=livros_menu)

# Menu de Ajuda
ajuda_menu = tk.Menu(menubar, tearoff = 0)
ajuda_menu.add_command(label="Sobre", command = sobre)
menubar.add_cascade(label="Ajuda", menu=ajuda_menu)
root.config(menu=menubar)

# Configurações da janela
largura_janela = 600
altura_janela = 450
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
pos_x = (largura_tela // 2) - (largura_janela // 2)
pos_y = (altura_tela // 2) - (altura_janela // 2)
root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

mostrar_frame(frame1)  # Começa no frame de salvar autor

root.mainloop()