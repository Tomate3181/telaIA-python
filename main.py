import customtkinter as ctk
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Configuração da Aparência e API ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except AttributeError:
    print("Erro: Chave da API do Gemini não encontrada.")
    exit()

# --- Classe Principal da Aplicação ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chatbot Gemini Estilizado")
        self.geometry("700x550")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Frame de Chat com Rolagem (A GRANDE MUDANÇA) ---
        self.tela_chat = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.tela_chat.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # Configura a coluna dentro do frame de rolagem para expandir
        self.tela_chat.grid_columnconfigure(0, weight=1)

        # --- Frame de Entrada de Texto ---
        self.input_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entrada_usuario = ctk.CTkEntry(self.input_frame, placeholder_text="Digite sua mensagem...", font=("Calibri", 14), corner_radius=10)
        self.entrada_usuario.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        self.entrada_usuario.bind("<Return>", self.enviar_mensagem)

        self.botao_enviar = ctk.CTkButton(self.input_frame, text="Enviar", font=("Calibri", 14, "bold"), width=100, corner_radius=10, command=self.enviar_mensagem)
        self.botao_enviar.grid(row=0, column=1, pady=5, sticky="e")

    def enviar_mensagem(self, event=None):
        mensagem_usuario = self.entrada_usuario.get().strip()
        if not mensagem_usuario:
            return

        self._adicionar_mensagem("Você", mensagem_usuario)
        self.entrada_usuario.delete(0, ctk.END)

        self.after(500, self.obter_resposta_gemini, mensagem_usuario)

    def obter_resposta_gemini(self, mensagem):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(mensagem)
            self._adicionar_mensagem("Gemini", response.text)
        except Exception as e:
            self._adicionar_mensagem("Erro", f"Ocorreu um erro: {e}")

    def _adicionar_mensagem(self, autor, texto):
        if autor == "Você":
            # Balão do Usuário (à direita)
            cor_balao = "#2b59c3" # Um azul mais escuro
            alinhamento = "e" # Leste (direita)
        else:
            # Balão do Gemini/Erro (à esquerda)
            cor_balao = "#333333" # Cinza escuro
            alinhamento = "w" # Oeste (esquerda)

        # Frame para alinhar o balão
        frame_alinhador = ctk.CTkFrame(self.tela_chat, fg_color="transparent")
        frame_alinhador.pack(fill="x", padx=5, pady=2, anchor=alinhamento)

        # O balão em si (um Label)
        balao = ctk.CTkLabel(
            frame_alinhador,
            text=texto,
            fg_color=cor_balao,
            corner_radius=15,
            font=("Calibri", 14),
            wraplength=self.winfo_width() - 100, # Quebra de linha automática
            justify="left" # Justifica o texto dentro do balão
        )
        balao.pack(padx=10, pady=5, anchor=alinhamento)

        # Força a atualização da interface e rola para o final
        self.update_idletasks()
        self.tela_chat._parent_canvas.yview_moveto(1.0)


if __name__ == "__main__":
    app = App()
    app.mainloop()