import customtkinter as ctk

import google.generativeai as genai

import json
import os
from dotenv import load_dotenv

# --- Configuração da Aparência e API (Movido para o início) ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

load_dotenv()
try:
    # A chave da API do Google agora é configurada aqui
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except (AttributeError, TypeError):
    print("Erro: Chave da API do Google (GOOGLE_API_KEY) não encontrada no arquivo .env")
    # Considerar sair do programa se a API for essencial
    # exit()

# --- Funções para Manipular o Arquivo de Usuários (usuarios.json) ---
def carregar_usuarios():
    """Carrega os usuários do arquivo JSON."""
    if not os.path.exists("usuarios.json"):
        return []
    try:
        with open("usuarios.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def salvar_usuarios(usuarios):
    """Salva a lista de usuários no arquivo JSON."""
    with open("usuarios.json", "w", encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

# --- CLASSE PRINCIPAL E ÚNICA DA APLICAÇÃO ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Atributo para guardar o nome do usuário logado
        self.nome_usuario = ""

        # A aplicação começa mostrando a tela de login
        self.mostrar_tela_login()

    # ==================================================================
    # MÉTODOS DA TELA DE LOGIN E CADASTRO
    # ==================================================================
    def mostrar_tela_login(self):
        """Cria e exibe os widgets da tela de login."""
        self.title("Chatbot - Tela de Login")
        self.geometry("400x450")
        self.resizable(False, False)
        
        # Limpa widgets de telas anteriores (se houver)
        for widget in self.winfo_children():
            widget.destroy()

        self.login_frame = ctk.CTkFrame(self, corner_radius=15)
        self.login_frame.pack(padx=20, pady=20, expand=True, fill="both")

        ctk.CTkLabel(self.login_frame, text="Bem-vindo!", font=("Calibri", 24, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(self.login_frame, text="Faça login para continuar", font=("Calibri", 14)).pack(pady=(0, 20))

        self.email_entry = ctk.CTkEntry(self.login_frame, placeholder_text="E-mail", font=("Calibri", 14), width=250)
        self.email_entry.pack(pady=10)

        self.senha_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Senha", show="*", font=("Calibri", 14), width=250)
        self.senha_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self.login_frame, text="Entrar", font=("Calibri", 14, "bold"), width=250, command=self.validar_login)
        self.login_button.pack(pady=15)

        self.register_button = ctk.CTkButton(self.login_frame, text="Não tem uma conta? Cadastre-se", font=("Calibri", 12), fg_color="transparent", command=self.mostrar_tela_cadastro)
        self.register_button.pack(pady=(0, 20))

        self.login_error_label = ctk.CTkLabel(self.login_frame, text="", text_color="red", font=("Calibri", 12))
        self.login_error_label.pack()

    def mostrar_tela_cadastro(self):
        """Cria a tela de cadastro em uma nova janela (Toplevel)."""
        if hasattr(self, 'toplevel_cadastro') and self.toplevel_cadastro.winfo_exists():
            self.toplevel_cadastro.focus()
            return

        self.toplevel_cadastro = ctk.CTkToplevel(self)
        self.toplevel_cadastro.title("Cadastro de Usuário")
        self.toplevel_cadastro.geometry("400x400")
        self.toplevel_cadastro.resizable(False, False)
        self.toplevel_cadastro.transient(self)

        cadastro_frame = ctk.CTkFrame(self.toplevel_cadastro, corner_radius=15)
        cadastro_frame.pack(expand=True, padx=20, pady=20, fill="both")

        ctk.CTkLabel(cadastro_frame, text="Crie sua Conta", font=("Calibri", 20, "bold")).pack(pady=10)

        self.novo_nome_entry = ctk.CTkEntry(cadastro_frame, placeholder_text="Nome Completo", font=("Calibri", 14), width=250)
        self.novo_nome_entry.pack(pady=10)

        self.novo_email_entry = ctk.CTkEntry(cadastro_frame, placeholder_text="E-mail", font=("Calibri", 14), width=250)
        self.novo_email_entry.pack(pady=10)

        self.nova_senha_entry = ctk.CTkEntry(cadastro_frame, placeholder_text="Senha", show="*", font=("Calibri", 14), width=250)
        self.nova_senha_entry.pack(pady=10)

        ctk.CTkButton(cadastro_frame, text="Cadastrar", font=("Calibri", 14, "bold"), width=250, command=self.cadastrar_usuario).pack(pady=15)

        self.cadastro_info_label = ctk.CTkLabel(cadastro_frame, text="", font=("Calibri", 12))
        self.cadastro_info_label.pack()

    def cadastrar_usuario(self):
        """Valida e salva os dados do novo usuário."""
        nome = self.novo_nome_entry.get().strip()
        email = self.novo_email_entry.get().strip()
        senha = self.nova_senha_entry.get().strip()

        if not nome or not email or not senha:
            self.cadastro_info_label.configure(text="Todos os campos são obrigatórios.", text_color="red")
            return

        usuarios = carregar_usuarios()
        if any(usuario['email'] == email for usuario in usuarios):
            self.cadastro_info_label.configure(text="Este e-mail já está cadastrado.", text_color="red")
            return

        novo_usuario = {"nome": nome, "email": email, "senha": senha}
        usuarios.append(novo_usuario)
        salvar_usuarios(usuarios)

        self.cadastro_info_label.configure(text="Cadastro realizado com sucesso!", text_color="green")
        self.toplevel_cadastro.after(2000, self.toplevel_cadastro.destroy)

    def validar_login(self):
        """Valida as credenciais do usuário e transita para a tela de chat."""
        email = self.email_entry.get()
        senha = self.senha_entry.get()

        if not email or not senha:
            self.login_error_label.configure(text="Preencha todos os campos.")
            return

        usuarios = carregar_usuarios()
        for usuario in usuarios:
            if usuario['email'] == email and usuario['senha'] == senha:
                self.login_error_label.configure(text="")
                # GUARDA O NOME DO USUÁRIO E CHAMA A TELA DE CHAT
                self.nome_usuario = usuario['nome']
                self.mostrar_tela_chat() 
                return

        self.login_error_label.configure(text="E-mail ou senha inválidos.")

    # ==================================================================
    # MÉTODOS DA TELA DE CHAT
    # ==================================================================
    def mostrar_tela_chat(self):
        """Limpa a janela e desenha a interface do chat."""
        # Limpa os widgets da tela de login
        for widget in self.winfo_children():
            widget.destroy()

        # Reconfigura a janela para o chat
        self.title(f"Chatbot Gemini - Logado como {self.nome_usuario}")
        self.geometry("700x550")
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Faz a área do chat expandir

        # --- Frame Superior para Título e Botões de Ação ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1) # Coluna do título expande

        self.chat_title = ctk.CTkLabel(self.top_frame, text="IA Própria - Chat", font=("Calibri", 18, "bold"))
        self.chat_title.grid(row=0, column=0, padx=(10, 0), sticky="w")

        self.botao_limpar = ctk.CTkButton(self.top_frame, text="Limpar", width=80, command=self.limpar_chat)
        self.botao_limpar.grid(row=0, column=1, padx=5)
        
        self.botao_tema = ctk.CTkButton(self.top_frame, text="Alternar Tema", width=120, command=self.alternar_tema)
        self.botao_tema.grid(row=0, column=2, padx=(0, 10))

        # --- Frame de Chat com Rolagem ---
        # Agora na linha 1
        self.tela_chat = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.tela_chat.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tela_chat.grid_columnconfigure(0, weight=1)
        
        # Faz a linha do chat (agora linha 1) expandir verticalmente
        self.grid_rowconfigure(1, weight=1) 

        # --- Frame de Entrada de Texto ---
        # Agora na linha 2
        self.input_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entrada_usuario = ctk.CTkEntry(self.input_frame, placeholder_text="Digite sua mensagem...", font=("Calibri", 14), corner_radius=10)
        self.entrada_usuario.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        self.entrada_usuario.bind("<Return>", self.enviar_mensagem)

        self.botao_enviar = ctk.CTkButton(self.input_frame, text="Enviar", font=("Calibri", 14, "bold"), width=100, corner_radius=10, command=self.enviar_mensagem)
        self.botao_enviar.grid(row=0, column=1, pady=5, sticky="e")

    def alternar_tema(self):
        """Muda o tema da aplicação entre 'dark' e 'light'."""
        novo_tema = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(novo_tema)
        
    def limpar_chat(self):
        """Remove todas as mensagens da tela de chat."""
        for widget in self.tela_chat.winfo_children():
            widget.destroy()

    def enviar_mensagem(self, event=None):
        mensagem_usuario = self.entrada_usuario.get().strip()
        if not mensagem_usuario:
            return

        # USA O NOME DO USUÁRIO LOGADO
        self._adicionar_mensagem(self.nome_usuario, mensagem_usuario)
        self.entrada_usuario.delete(0, ctk.END)

        self.after(500, self.obter_resposta_gemini, mensagem_usuario)

    def obter_resposta_gemini(self, mensagem):
        try:
            model = genai.GenerativeModel('gemini-2.5-pro') # Usando um modelo padrão
            response = model.generate_content(mensagem)
            self._adicionar_mensagem("Gemini", response.text)
        except Exception as e:
            self._adicionar_mensagem("Erro", f"Ocorreu um erro: {e}")

    def _adicionar_mensagem(self, autor, texto):
        # AQUI USAMOS O NOME DO USUÁRIO PARA DEFINIR O BALÃO
        if autor == self.nome_usuario:
            cor_balao = "#2b59c3"
            alinhamento = "e"
            justificativa_texto = "right"
        else:
            cor_balao = "#333333"
            alinhamento = "w"
            justificativa_texto = "left"

        frame_alinhador = ctk.CTkFrame(self.tela_chat, fg_color="transparent")
        frame_alinhador.pack(fill="x", padx=10, pady=4, anchor=alinhamento)

        # Adiciona o nome do autor acima do balão
        ctk.CTkLabel(frame_alinhador, text=autor, font=("Calibri", 12, "italic")).pack(anchor=alinhamento, padx=10)

        balao = ctk.CTkLabel(
            frame_alinhador,
            text=texto,
            fg_color=cor_balao,
            corner_radius=15,
            font=("Calibri", 14),
            wraplength=self.winfo_width() - 150,
            justify=justificativa_texto,
            padx=10,
            pady=10,
            text_color="#EAEAEA"
        )
        balao.pack(anchor=alinhamento, padx=5)

        self.update_idletasks()
        self.tela_chat._parent_canvas.yview_moveto(1.0)

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    app = App()
    app.mainloop()