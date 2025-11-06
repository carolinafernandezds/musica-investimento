import pandas as pd
import matplotlib.pyplot as plt
import sys

# --- 1. ENTRADA DE DADOS (Leitura do arquivo gerado) ---
nome_arquivo_entrada = 'previsoes_finais.csv'
print(f"Lendo dados de previsão de '{nome_arquivo_entrada}'...")

try:
    df_resultados = pd.read_csv(nome_arquivo_entrada, index_col='Ticker')
except FileNotFoundError:
    print(f"\n[ERRO CRÍTICO] Arquivo '{nome_arquivo_entrada}' não encontrado!")
    print("Por favor, execute o script 'previsao_geral.py' primeiro para gerar os dados.")
    sys.exit() # Encerra o script
except Exception as e:
    print(f"[ERRO] Não foi possível ler o arquivo: {e}")
    sys.exit() # Encerra o script

print("Dados de previsão carregados com sucesso.\n")


# --- 2. ASSUMPÇÕES E CLASSIFICAÇÃO DE ATIVOS ---

# 2.1. Definir Retorno e Volatilidade para a Renda Fixa (CDI)
# Assumindo Selic de 10% a.a. -> ~0.038% ao dia (assumindo 252 dias úteis)
retorno_cdi_42d = 0.038 
vol_cdi_42d = 0.01 # Volatilidade do CDI é próxima de zero

# Adicionar CDI ao DataFrame com as 3 colunas existentes
df_resultados.loc['CDI'] = [
    retorno_cdi_42d, 
    vol_cdi_42d, 
    retorno_cdi_42d / vol_cdi_42d
]

# 2.2. Classificar todos os ativos
def classificar_ativo(ticker):
    if ticker in ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD']:
        return 'Cripto'
    if ticker == 'CDI':
        return 'RendaFixa'
    # Todos os outros (Ações, ETFs, FIIs, Câmbio) são tratados como Renda Variável
    return 'Variavel'

# Agora, crie a nova coluna 'Classe' para todos os ativos, incluindo o CDI
df_resultados['Classe'] = df_resultados.index.map(classificar_ativo)

# 2.3. Filtrar e Ordenar os melhores por classe
# Apenas seleciona ativos com Retorno/Risco positivo para investimento
df_variavel = df_resultados[
    (df_resultados['Classe'] == 'Variavel') & (df_resultados['Retorno_Vol_Ratio'] > 0)
].sort_values(by='Retorno_Vol_Ratio', ascending=False)

df_cripto = df_resultados[
    (df_resultados['Classe'] == 'Cripto') & (df_resultados['Retorno_Vol_Ratio'] > 0)
].sort_values(by='Retorno_Vol_Ratio', ascending=False)

df_renda_fixa = df_resultados[df_resultados['Classe'] == 'RendaFixa']

# --- 3. DEFINIÇÃO DAS CARTEIRAS ---

# Quantos ativos de cada classe vamos selecionar?
TOP_N_VARIAVEL = 5  # Top 5 ações/ETFs/etc. com Retorno/Risco positivo
TOP_N_CRIPTO = 2    # Top 2 criptos com Retorno/Risco positivo

# Estrutura das carteiras
portfolios = {
    'Conservador': {
        'RendaFixa': 0.75,
        'Variavel': 0.25,
        'Cripto': 0.0
    },
    'Moderado': {
        'RendaFixa': 0.45,
        'Variavel': 0.50,
        'Cripto': 0.05
    },
    'Arrojado': {
        'RendaFixa': 0.20,
        'Variavel': 0.70,
        'Cripto': 0.10
    }
}

plt.style.use('seaborn-v0_8-darkgrid')

# --- 4. GERAÇÃO E ANÁLISE DAS CARTEIRAS ---

print("--- Geração das Carteiras Otimizadas (Próximos 42 dias) ---")
print(f"Critério: Top {TOP_N_VARIAVEL} Renda Variável, Top {TOP_N_CRIPTO} Cripto (Apenas com Retorno/Risco > 0)\n")

for nome_carteira, alocacao in portfolios.items():
    print(f"\n========================================================")
    print(f"MONTANDO CARTEIRA: {nome_carteira.upper()}")
    print("========================================================")
    
    carteira_detalhada = [] # (Ticker, Peso)
    
    # 1. Alocação em Renda Fixa
    peso_rf = alocacao['RendaFixa']
    if peso_rf > 0:
        carteira_detalhada.append(('CDI', peso_rf))
        
    # 2. Alocação em Renda Variável
    peso_total_rv = alocacao['Variavel']
    if peso_total_rv > 0:
        ativos_rv_selecionados = df_variavel.head(TOP_N_VARIAVEL)
        if ativos_rv_selecionados.empty:
            print("AVISO: Nenhum ativo de Renda Variável com Retorno/Risco positivo encontrado. Alocando em CDI.")
            carteira_detalhada.append(('CDI', peso_total_rv)) # Aloca o peso extra no CDI
        else:
            peso_por_ativo_rv = peso_total_rv / len(ativos_rv_selecionados)
            print(f"\nAlocando {peso_total_rv*100:.0f}% em Renda Variável (Top {len(ativos_rv_selecionados)}):")
            for ticker in ativos_rv_selecionados.index:
                print(f"  - {ticker}: {peso_por_ativo_rv*100:.2f}%")
                carteira_detalhada.append((ticker, peso_por_ativo_rv))
            
    # 3. Alocação em Cripto
    peso_total_cripto = alocacao['Cripto']
    if peso_total_cripto > 0:
        ativos_cripto_selecionados = df_cripto.head(TOP_N_CRIPTO)
        if ativos_cripto_selecionados.empty:
            print("AVISO: Nenhuma Cripto com Retorno/Risco positivo encontrada. Alocando em CDI.")
            carteira_detalhada.append(('CDI', peso_total_cripto)) # Aloca o peso extra no CDI
        else:
            peso_por_ativo_cripto = peso_total_cripto / len(ativos_cripto_selecionados)
            print(f"\nAlocando {peso_total_cripto*100:.0f}% em Cripto (Top {len(ativos_cripto_selecionados)}):")
            for ticker in ativos_cripto_selecionados.index:
                print(f"  - {ticker}: {peso_por_ativo_cripto*100:.2f}%")
                carteira_detalhada.append((ticker, peso_por_ativo_cripto))
            
    # 4. Cálculo Ponderado da Carteira
    retorno_carteira = 0.0
    volatilidade_carteira = 0.0 # CÁLCULO SIMPLIFICADO! (ignora correlação)
    
    # Agrupador para o gráfico (para o caso de alocação extra em CDI)
    carteira_grafico = {}
    
    for ticker, peso in carteira_detalhada:
        retorno_ativo = df_resultados.loc[ticker, 'Retorno_Medio_42d']
        vol_ativo = df_resultados.loc[ticker, 'Volatilidade_Media_42d']
        
        retorno_carteira += peso * retorno_ativo
        volatilidade_carteira += peso * vol_ativo
        
        # Agrega os pesos por ticker (ex: CDI 75% + CDI 25% = CDI 100%)
        carteira_grafico[ticker] = carteira_grafico.get(ticker, 0) + peso
        
    labels_grafico = [f"{ticker} ({peso*100:.1f}%)" for ticker, peso in carteira_grafico.items()]
    sizes_grafico = list(carteira_grafico.values())
        
    # 5. Exibir Resultados (apenas no console, o gráfico mostrará o principal)
    print("\n--- Resultado Ponderado (detalhes no console) ---")
    print(f"Retorno Esperado (42d): {retorno_carteira:.4f}%")
    print(f"Volatilidade Esperada (42d): {volatilidade_carteira:.4f}% (Simplificada)")
    print("--------------------------------------------------")
    
    
    # 6. Gerar Gráfico de Pizza
    fig, ax = plt.subplots(figsize=(10, 7))
    
    patches, texts, autotexts = ax.pie(
        sizes_grafico, 
        autopct='%1.1f%%',
        startangle=90, 
        pctdistance=0.85 # Distância do texto automático do centro
    )
    # Formata os textos dos percentuais dentro da pizza
    for text in texts + autotexts:
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_color('white')

    ax.set_title(f"Composição da Carteira: {nome_carteira}", fontsize=16, pad=20)
    
    # --- BLOCO MODIFICADO: Adiciona o texto com os resultados ponderados acima da legenda ---
    texto_resultado = (
        f"Resultados Esperados (42d):\n"
        f"Retorno: {retorno_carteira:.4f}%\n"
        f"Volatilidade: {volatilidade_carteira:.4f}%"
    )
    
    ax.text(
        1.02, 0.95, # Ajuste a posição X e Y para ficar acima da legenda
        texto_resultado,
        transform=ax.transAxes, # Usa coordenadas relativas ao eixo
        fontsize=10,
        verticalalignment='top', # Alinhamento vertical superior
        horizontalalignment='left', # Alinhamento horizontal esquerdo
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "white", "edgecolor": "lightgray", "alpha": 0.9} # Caixa de texto melhorada
    )
    # --- FIM DO BLOCO MODIFICADO ---

    # Adiciona legenda dos ativos
    ax.legend(
        labels_grafico,
        title="Ativos (Alocação)", # Adiciona um título para a legenda
        loc='center left',
        bbox_to_anchor=(1.02, 0.5), # Reposiciona a legenda um pouco mais para baixo
        fontsize=9,
        title_fontsize=10
    )
    
    # Ajusta o layout para garantir que tudo caiba
    plt.tight_layout(rect=[0, 0, 0.8, 1]) # Ajusta a área da pizza para a legenda caber
    
    # Salva o gráfico
    nome_grafico = f"carteira_{nome_carteira.lower()}.png"
    plt.savefig(nome_grafico, dpi=300) # Aumenta o DPI para melhor qualidade
    print(f"Gráfico salvo como: '{nome_grafico}'")
    plt.close(fig)