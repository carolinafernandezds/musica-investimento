import streamlit as st
import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# ==============================
# CONFIGURAÇÕES INICIAIS
# ==============================
CLIENT_ID = "714e12ef967d488f8998247e19b9c6a0"
CLIENT_SECRET = "76b7c12d373d4de5ad056821f6786e3f"
REDIRECT_URI = "http://127.0.0.1:8501" 
SCOPE = "user-top-read user-read-private"

st.set_page_config(page_title="Meu Perfil Musical x Investidor", page_icon="🎧", layout="wide") # Layout amplo

# --- LÓGICA DE NAVEGAÇÃO MELHORADA ---
# Obter o código da URL ANTES de decidir a página
query_params = st.query_params
CODE = query_params.get("code", [None])[0] if "code" in query_params else None

# Controle de navegação
if "page" not in st.session_state:
    # Se temos um código na URL, viemos do Spotify, vá para o perfil
    if CODE:
        st.session_state.page = "perfil"
    else:
        st.session_state.page = "home"
# --- FIM DA LÓGICA DE NAVEGAÇÃO ---

def go_to(page_name):
    st.session_state.page = page_name

# ==============================
# CSS - ESTILO MODERNO
# ==============================
st.markdown("""
<style>
:root {
  --roxo: #6c5ce7;
  --roxo-escuro: #341f97;
  --fundo: linear-gradient(135deg, #1e1b4b, #4c1d95);
}
            
[data-testid="stHeader"] {
  background-color: transparent;
}

[data-testid="stAppViewContainer"] {
  background: var(--fundo);
  color: #fff;
  font-family: "Inter", sans-serif;
}

h1, h2, h3, h4 {
  color: #c4b5fd;
  font-weight: 600;
}

/* Subheaders (para o título da tabela) */
h2 {
    text-align: center;
    margin-bottom: 1.5rem;
}

a, a:visited {
  color: #a78bfa;
  text-decoration: none;
}

.block-container {
  padding-top: 3rem;
  padding-bottom: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

/* Parágrafo do header */
.header p {
  color:#d1c4f3;
  max-width:600px;
  margin:0 auto;
}

.card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
  backdrop-filter: blur(6px);
  max-width: 600px; /* Largura máxima mantida */
  margin: 0 auto; /* Centraliza o card */
  margin-bottom: 1.5rem; /* Espaço inferior */
  /* Garante altura mínima para alinhar com a tabela */
  height: 100%; 
}

.perfil {
  font-size: 2rem;
  font-weight: bold;
  margin-top: 1rem;
}

.perfil.agressivo { color: #ff7675; }
.perfil.moderado { color: #fdcb6e; }
.perfil.conservador { color: #55efc4; }

.user-card {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 15px; /* Menor */
    padding: 0.8rem 1.5rem; /* Menor */
    text-align: center;
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
    backdrop-filter: blur(6px);
    max-width: 450px; /* Mais estreito */
    margin: 0 auto;
    margin-bottom: 2rem;
    color: #ede9fe; /* Cor do texto */
    font-size: 1rem; /* Tamanho da fonte */
    font-weight: 500; /* Peso da fonte mais suave */
}

/* Este é o container que o Streamlit cria para st.button() */
[data-testid="stButton"] {
    /* --- ATUALIZAÇÃO: Regra de centralização mais forte --- */
    /* Usa flex para centralizar o botão filho */
    display: flex;
    justify-content: center;
    width: 100%; /* O container ocupa 100% */
    margin-top: 1.5rem; /* Adiciona um espaço acima */
}

/* Este é o botão real dentro do container */
[data-testid="stButton"] button {
    background-color: var(--roxo);
    color: white !important; /* Usa !important para garantir que o texto padrão do streamlit seja sobrescrito */
    border: 1px solid var(--roxo-escuro);
    border-radius: 30px;
    padding: 1rem 2.2rem; /* Aumentado */
    font-size: 1.15rem; /* CORRIGIDO: Estava 4.15rem, voltei para 1.15rem */
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: "Inter", sans-serif !important; /* Garante a fonte */
}

/* Efeito hover para os botões do Streamlit */
[data-testid="stButton"] button:hover {
    background-color: #8e7cf0;
    border-color: #a78bfa;
}

button.spotify-btn {
  background-color: #6c5ce7;
  border: none;
  border-radius: 30px;
  padding: 1rem 2.2rem; /* Aumentado */
  color: white;
  font-size: 1.15rem; /* Aumentado */
  cursor: pointer;
  transition: all 0.3s ease;
}

button.spotify-btn:hover {
  background-color: #8e7cf0;
}

[data-testid="stDataFrame"] {
    /* Remove a borda padrão do streamlit */
    border: none;
    border-radius: 15px; /* Arredonda as pontas */
}

/* Container principal da tabela */
[data-testid="stDataFrame"] .main-container {
    background: rgba(255, 255, 255, 0.08); /* Fundo de vidro, igual ao .card */
    border: 1px solid rgba(255, 255, 255, 0.15);
}

/* Cabeçalho da tabela (ex: "Valor") */
[data-testid="stDataFrame"] thead th {
    background-color: rgba(0, 0, 0, 0.2); /* Um pouco mais escuro */
    color: #c4b5fd; /* Cor do título roxo */
    font-size: 1rem;
    text-transform: uppercase; /* Deixa em maiúsculo */
}

/* Células da tabela (corpo) */
[data-testid="stDataFrame"] tbody td {
    color: white; /* Texto branco */
    font-size: 1rem;
}

/* Células de índice (ex: "mean_energy") */
[data-testid="stDataFrame"] tbody th {
    background-color: rgba(0, 0, 0, 0.1);
    color: #d1c4f3; /* Cor do parágrafo roxo */
    font-weight: 500;
}

/* Remove a barra de ferramentas da tabela */
[data-testid="stDataFrame"] [data-testid="stElementToolbar"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def coletar_dados_usuario(sp, limit=100):
    """Coleta as top 100 tracks do usuário e suas features de áudio."""
    try:
        top = sp.current_user_top_tracks(limit=limit, time_range="long_term")
        if not top or not top.get("items"):
            st.warning("Não foi possível obter suas músicas. Você já ouviu algo no Spotify recentemente?")
            return None, None
            
        track_ids = [t["id"] for t in top["items"]]
        features = sp.audio_features(track_ids)
        
        # Filtra features inválidas (None)
        valid_features = [f for f in features if f is not None]

        if not valid_features:
            st.warning("Não foi possível obter as características das suas músicas.")
            return None, None
            
        df = pd.DataFrame(valid_features)
        
        agg = {
            "mean_energy": df["energy"].mean(),
            "mean_bpm": df["tempo"].mean(),
            "mean_instrumentalness": df["instrumentalness"].mean(),
            "mean_acousticness": df["acousticness"].mean(),
            "mean_valence": df["valence"].mean(),
            # O desvio padrão só é calculado se houver dados suficientes
            "std_valence": df["valence"].std() if len(df["valence"]) > 1 else 0
        }
        return agg, df
    except Exception as e:
        st.error(f"Erro ao coletar dados do Spotify: {e}")
        return None, None


def classificar_regra(data):
    """Classifica o perfil de investidor com base nas features de áudio."""
    if data["mean_energy"] > 0.7 and data["mean_bpm"] > 120 and data["mean_instrumentalness"] < 0.2:
        return "Agressivo", "agressivo"
    elif data["mean_acousticness"] > 0.6 and data["mean_valence"] > 0.6 and data["std_valence"] < 0.15:
        return "Conservador", "conservador"
    else:
        return "Moderado", "moderado"

# ==============================
# HOME PAGE
# ==============================
if st.session_state.page == "home":
    st.markdown("""
    <div class="header">
        <h1>Quer descobrir seu perfil de investidor<br>a partir das suas músicas mais ouvidas no Spotify?</h1>
        <p>
        Nosso algoritmo analisa o ritmo, energia e emoções das suas músicas favoritas e mapeia isso para o seu perfil investidor.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- ATUALIZAÇÃO: Forçando a centralização com colunas ---
    col1, col2, col3 = st.columns([1, 1, 1]) 

    with col2:
        if st.button("🎧 Descobrir meu perfil agora"):
            go_to("perfil")
            st.rerun() # Garante a atualização imediata da página

# ==============================
# PERFIL PAGE (ANÁLISE)
# ==============================
elif st.session_state.page == "perfil":
    st.markdown("""
    <div class="header">
      <h1>Perfil Musical → Perfil de Investidor</h1>
      <p>Conecte-se ao Spotify para continuar.</p>
    </div>
    """, unsafe_allow_html=True)

    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True
    )

    # O CODE já foi pego lá em cima
    if not CODE:
        auth_url = auth_manager.get_authorize_url()
        st.markdown(f"""
        <div class='card'>
            <a href='{auth_url}' target='_self'>
                <button class='spotify-btn'>Conectar com Spotify</button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⬅ Voltar"):
            go_to("home")
            st.rerun()
        st.stop()

    else:
        try:
            with st.spinner("Conectando ao Spotify e analisando seu perfil..."):
                token_info = auth_manager.get_access_token(CODE, as_dict=True)
                sp = Spotify(auth=token_info["access_token"])
                user = sp.current_user()
                
                # Coleta os dados reais
                data, df_raw = coletar_dados_usuario(sp)
            
            # Mostrar o usuário logado
            st.markdown(f"<div class='user-card'>Logado no Spotify como: {user['display_name']}</div>", unsafe_allow_html=True)

            if data:
                # 1. Classifica o perfil
                perfil_texto, classe = classificar_regra(data)
                
                # 2. Define descrição e carteira com base no perfil
                profile_description = ""
                profile_portfolio = ""
                if perfil_texto == "Agressivo":
                    profile_description = "Você gosta de músicas com alta energia e ritmo acelerado. Isso sugere que você é dinâmico, aceita mais riscos e está sempre em busca de novidades."
                    profile_portfolio = "Carteira Sugerida: 70% Ações, 20% Renda Fixa, 10% Cripto"
                elif perfil_texto == "Moderado":
                    profile_description = "Seu gosto é eclético, misturando momentos de energia com faixas mais calmas. Você busca equilíbrio, sendo alguém que planeja, mas se permite alguma flexibilidade."
                    profile_portfolio = "Carteira Sugerida: 50% Ações, 45% Renda Fixa, 5% Cripto"
                else: # Conservador
                    profile_description = "Você prefere músicas mais acústicas, orgânicas e com emoção estável. Isso indica um perfil mais cauteloso, que valoriza a segurança e a consistência."
                    profile_portfolio = "Carteira Sugerida: 25% Ações, 75% Renda Fixa"

                # 3. Exibe os resultados em colunas
                col1, col2 = st.columns([2, 3]) # Coluna da esquerda (2 partes) e direita (3 partes)

                with col1:
                    st.subheader("Características Médias") 
                    display_df = pd.DataFrame(data, index=["Valor"]).T.rename(columns={0: "Valor"})
                    # O CSS novo vai estilizar isso automaticamente
                    st.dataframe(display_df)

                with col2:
                    # O cartão do perfil vai na coluna da direita
                    st.markdown(f"""
                    <div class='card'>
                        <h3>Seu perfil investidor:</h3>
                        <div class='perfil {classe}'>{perfil_texto}</div>
                        <p style='margin-top: 1.5rem; color: #d1c4f3; text-align: left;'>
                            {profile_description}
                        </p>
                        <p style='margin-top: 1rem; color: #c4b5fd; text-align: left; font-weight: 600; font-size: 1.1rem;'>
                            {profile_portfolio}
                        </p>
                        
                    </div>
                    """, unsafe_allow_html=True)
                
            else:
                # Se 'data' for None (porque o usuário não tem músicas)
                st.warning("Não foi possível obter dados musicais suficientes do seu perfil. Tente ouvir mais músicas e volte depois!")

        except Exception as e:
            st.error(f"Erro ao obter token de acesso ou processar dados. Tente voltar e reconectar. (Detalhe: {e})")
        
        # Botão de voltar fica abaixo das colunas
        if st.button("⬅ Voltar"):
            go_to("home")
            st.rerun()
