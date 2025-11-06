import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(page_title="Meu Perfil Musical x Investidor", page_icon="🎧", layout="wide")


query_params = st.query_params

if "page" not in st.session_state:
    
    st.session_state.page = "home"


def go_to(page_name):
    st.session_state.page = page_name


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

h1, h2, h3, h4, h5 {
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

/* CSS para os inputs de texto dentro do card */
.card [data-testid="stTextInput"] {
    margin-bottom: 0.75rem; /* Espaço entre os inputs */
}
.card [data-testid="stTextInput"] input {
    background-color: rgba(255, 255, 255, 0.1); /* Fundo leve */
    border: 1px solid rgba(255, 255, 255, 0.2); /* Borda sutil */
    color: #fff; /* Texto branco */
    border-radius: 10px; /* Menos arredondado que o botão */
}
/* Cor do placeholder */
.card [data-testid="stTextInput"] input::placeholder {
    color: rgba(255, 255, 255, 0.5);
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
    display: flex;
    justify-content: center;
    width: 100%; /* O container ocupa 100% */
    margin-top: 1.5rem; /* Adiciona um espaço acima */
}

/* Este é o botão real dentro do container */
[data-testid="stButton"] button {
    background-color: var(--roxo);
    color: white !important; 
    border: 1px solid var(--roxo-escuro);
    border-radius: 30px;
    padding: 1rem 2.2rem; 
    font-size: 1.15rem; 
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: "Inter", sans-serif !important; 
}

[data-testid="stButton"] button:hover {
    background-color: #8e7cf0;
    border-color: #a78bfa;
}

/* Botão de conexão (legado, mantido para referência se necessário) */
button.spotify-btn {
  background-color: #6c5ce7;
  border: none;
  border-radius: 30px;
  padding: 1rem 2.2rem;
  color: white;
  font-size: 1.15rem;
  cursor: pointer;
  transition: all 0.3s ease;
}
button.spotify-btn:hover {
  background-color: #8e7cf0;
}

[data-testid="stDataFrame"] {
    border: none;
    border-radius: 15px; 
}

[data-testid="stDataFrame"] .main-container {
    background: rgba(255, 255, 255, 0.08); 
    border: 1px solid rgba(255, 255, 255, 0.15);
}

[data-testid="stDataFrame"] thead th {
    background-color: rgba(0, 0, 0, 0.2); 
    color: #c4b5fd; 
    font-size: 1rem;
    text-transform: uppercase; 
}

[data-testid="stDataFrame"] tbody td {
    color: white; 
    font-size: 1rem;
}

[data-testid="stDataFrame"] tbody th {
    background-color: rgba(0, 0, 0, 0.1);
    color: #d1c4f3; 
    font-weight: 500;
}

[data-testid="stDataFrame"] [data-testid="stElementToolbar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)


def simular_dados_pelas_musicas(song_list):
    try:
            
        df = pd.read_csv('spotify_data.csv')
        
        df['track_name_clean'] = df['track_name'].str.strip().str.lower()
        
    except Exception as e:
        print(f"Erro ao ler ou processar o CSV: {e}")
        return None

    valid_songs_clean = [s.strip().lower() for s in song_list if s and s.strip()]
    
    if not valid_songs_clean:
        print("Nenhuma música válida fornecida na lista de entrada.")
        return None

    musicas_encontradas_df = df[df['track_name_clean'].isin(valid_songs_clean)].copy()
    
    if musicas_encontradas_df.empty:
        print("Nenhuma música da sua lista foi encontrada no CSV.")
        return None
    
    audio_features = [
        'danceability', 'energy', 'acousticness', 'instrumentalness', 
        'liveness', 'valence', 'tempo', 'loudness'
    ]
    
    medias = musicas_encontradas_df[audio_features].mean()

    data = {
        "mean_danceability": medias.get('danceability', np.nan),
        "mean_energy": medias.get('energy', np.nan),
        "mean_bpm": medias.get('tempo', np.nan),
        "mean_instrumentalness": medias.get('instrumentalness', np.nan),
        "mean_acousticness": medias.get('acousticness', np.nan),
        "mean_valence": medias.get('valence', np.nan),
        "mean_loudness": medias.get('loudness', np.nan),
    }

    
    
    return {k: v for k, v in data.items() if pd.notna(v)}
    
    
    return data



def classificar_regra(data):
    
    if data["mean_energy"] > 0.5 and data["mean_bpm"] > 125 and data["mean_acousticness"] < 0.45:
        return "Agressivo", "agressivo"
    elif data["mean_acousticness"] > 0.4 and data["mean_energy"] < 0.55:
        return "Conservador", "conservador"
    else:
        return "Moderado", "moderado"


if st.session_state.page == "home":
    st.markdown("""
    <div class="header">
        <h1>Quer descobrir seu perfil de investidor<br>a partir das suas músicas mais ouvidas no Spotify?</h1>
        <p>
        Nosso algoritmo analisa o ritmo, energia e emoções das suas músicas favoritas e mapeia isso para o seu perfil investidor.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1]) 

    with col2:
        if st.button("🎧 Descobrir meu perfil agora"):
            go_to("perfil")
            st.rerun() 


elif st.session_state.page == "perfil":
    st.markdown("""
    <div class="header">
      <h1>Perfil Musical → Perfil de Investidor</h1>
      <p>Insira até 5 músicas que você gosta para analisarmos seu perfil.</p>
    </div>
    """, unsafe_allow_html=True)

    
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>Quais músicas você curte?</h3>", unsafe_allow_html=True)


    song1 = st.text_input("Música 1", placeholder="Nome da Música 1", label_visibility="collapsed")
    song2 = st.text_input("Música 2", placeholder="Nome da Música 2", label_visibility="collapsed")
    song3 = st.text_input("Música 3", placeholder="Nome da Música 3", label_visibility="collapsed")
    song4 = st.text_input("Música 4", placeholder="Nome da Música 4", label_visibility="collapsed")
    song5 = st.text_input("Música 5", placeholder="Nome da Música 5", label_visibility="collapsed")
    
    if st.button("Analisar Perfil"):
        songs = [song1, song2, song3, song4, song5]
        
        data = simular_dados_pelas_musicas(songs)
        
        if data:
            
            st.session_state.analysis_data = data
            st.session_state.show_results = True
        else:
            
            st.warning("Não encontramos nenhuma música.")
            st.session_state.show_results = False
            
    st.markdown("</div>", unsafe_allow_html=True) 

    
    if st.session_state.get("show_results", False):
        try:
            data = st.session_state.analysis_data
            
            
            perfil_texto, classe = classificar_regra(data)
            
            
            profile_description = ""
            profile_portfolio = ""
            if perfil_texto == "Agressivo":
                profile_description = "Você gosta de músicas com alta energia e ritmo acelerado. Isso sugere que você é dinâmico, aceita mais riscos e está sempre em busca de novidades."
                profile_portfolio = "Carteira Sugerida: 70% Ações, 20% Renda Fixa, 10% Cripto"
            elif perfil_texto == "Moderado":
                profile_description = "Seu gosto é eclético, misturando momentos de energia com faixas mais calmas. Você busca equilíbrio, sendo alguém que planeja, mas se permite alguma flexibilidade."
                profile_portfolio = "Carteira Sugerida: 50% Ações, 45% Renda Fixa, 5% Cripto"
            else: 
                profile_description = "Você prefere músicas mais acústicas, orgânicas e com emoção estável. Isso indica um perfil mais cauteloso, que valoriza a segurança e a consistência."
                profile_portfolio = "Carteira Sugerida: 25% Ações, 75% Renda Fixa"

            col1, col2 = st.columns([2, 3]) 

            with col1:
                    st.subheader("Características Médias") 
                    display_df = pd.DataFrame(data, index=["Valor"]).T.rename(columns={0: "Valor"})
                
                    st.dataframe(display_df)

            with col2:
                    
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
            
        except Exception as e:
            st.error(f"Erro ao processar os dados simulados. (Detalhe: {e})")

    
    if st.button("⬅ Voltar"):
        
        keys_to_clear = ["show_results", "analysis_data"]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        go_to("home")
        st.rerun()