import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 0. CONFIGURAÇÃO DOS ATIVOS ---
# Lista de ativos para analisar (40 Tickers)
# --- 0. CONFIGURAÇÃO DOS ATIVOS ---
# Lista de ativos para analisar (40 Tickers) - VERSÃO CORRIGIDA
# --- 0. CONFIGURAÇÃO DOS ATIVOS ---
# Lista de ativos para analisar (40 Tickers) - VERSÃO CORRIGIDA 2
# --- 0. CONFIGURAÇÃO DOS ATIVOS ---
# Lista de ativos para analisar (40 Tickers) - VERSÃO CORRIGIDA 2
tickers_list = [
    # --- 1. Índices (Referência de Mercado) ---
    '^BVSP',       # Índice Ibovespa (Referência da bolsa)
    'XFIX11.SA',   # ETF que replica o IFIX (Substituindo ^IFIX)

    # --- 2. Blue Chips & Setores Principais (Bancos, Commodities, Indústria) ---
    'PETR4.SA',    # Petrobras (Petróleo e Gás)
    'PRIO3.SA',    # Prio (Petróleo e Gás - Privada)
    'VALE3.SA',    # Vale (Mineração)
    'SUZB3.SA',    # Suzano (Papel e Celulose)
    'MRFG3.SA',    # Marfrig (Alimentos / Proteína)
    'ITUB4.SA',    # Itaú Unibanco (Bancos)
    'BBDC4.SA',    # Bradesco (Bancos)
    'BBAS3.SA',    # Banco do Brasil (Bancos)
    'BPAC11.SA',   # BTG Pactual (Banco de Investimento)
    'B3SA3.SA',    # B3 (Mercado Financeiro/Infra)
    'WEGE3.SA',    # WEG (Indústria / Exportadora)
    'ABEV3.SA',    # Ambev (Consumo / Bebidas)

    # --- 3. Utilities (Setores Defensivos: Elétrico, Saneamento, Telecom) ---
    'ELET3.SA',    # Eletrobras (Elétrico / Geração)
    'EQTL3.SA',    # Equatorial (Elétrico / Distribuição)
    'CPLE6.SA',    # Copel (Elétrico / Integrada)
    'SBSP3.SA',    # Sabesp (Saneamento)
    'VIVT3.SA',    # Telefônica Brasil (Telecom)

    # --- 4. Varejo, Serviços e Tecnologia (Consumo Interno) ---
    'MGLU3.SA',    # Magazine Luiza (Varejo E-commerce)
    'RADL3.SA',    # Raia Drogasil (Varejo / Farmacêutico)
    'ASAI3.SA',    # Assaí (Varejo / Atacarejo)
    'LREN3.SA',    # Lojas Renner (Varejo / Vestuário) 
    'SMFT3.SA',    # Smartfit (Serviços / Academias)
    'RDOR3.SA',    # Rede D'Or (Saúde)

    # --- 5. Setores Específicos (Construção, Shoppings, Aéreo, Logística) ---
    'CYRE3.SA',    # Cyrela (Construção Civil)
    'MULT3.SA',    # Multiplan (Shoppings)
    'AZUL4.SA',    # Azul (Aéreo / Transporte)
    'RAIL3.SA',    # Rumo (Logística / Ferrovia)

    # --- 6. ETFs (Exposição Diversificada Global e Local) ---
    'IVVB11.SA',   # ETF do S&P 500 em Reais (EUA Geral)
    'NASD11.SA',   # ETF da NASDAQ-100 em Reais (EUA Tech)
    'XINA11.SA',   # ETF de Ações Chinesas em Reais (China)
    'SMAL11.SA',   # ETF de Small Caps (Brasil Menores)
    'BOVA11.SA',   # ETF que replica o Ibovespa (Brasil Geral)
    'GOLD11.SA',   # ETF de Ouro (Proteção / Commodity)

    # --- 7. Câmbio (Moedas) ---
    'USDBRL=X',    # Dólar Americano em Reais
    'EURBRL=X',    # Euro em Reais
    
    # --- 8. Criptomoedas (Alta Volatilidade) ---
    'BTC-USD',     # Bitcoin em Dólar
    'ETH-USD',     # Ethereum em Dólar
    'SOL-USD',     # Solana em Dólar
    'ADA-USD'      # Cardano em Dólar
]
# Período de análise
inicio = '2020-01-01'
fim = pd.to_datetime('today').strftime('%Y-%m-%d')

# Janelas para cálculo das métricas e para a previsão (lags)
janela_media_retorno = 21
janela_vol = 21
janela_prev = 90  # Lags usados no modelo

# Lista para guardar os resultados finais
resultados_finais = []

print("--- INICIANDO ANÁLISE AUTOREGRESSIVA DE MÚLTIPLOS ATIVOS ---")
print(f"Período: {inicio} a {fim}")
print(f"Janelas Móveis: {janela_media_retorno}d | Lags do Modelo: {janela_prev}d")
print("-------------------------------------------------------------\n")


# --- INÍCIO DO LOOP PRINCIPAL ---
for ticker in tickers_list:
    print(f"\n======== Processando Ticker: {ticker} ========")

    # --- 1. Coleta e Preparação dos Dados ---
    print(f"Baixando dados de {ticker} de {inicio} até {fim}...")
    try:
        dados_completos = yf.download(tickers=ticker, start=inicio, end=fim, auto_adjust=True, progress=False)

        if dados_completos.empty:
            print(f"\nERRO: O Yahoo Finance não retornou dados para {ticker}.")
            continue # Pula para o próximo ticker

        # Seleciona a coluna 'Close'
        ativo_close = dados_completos['Close'].squeeze()
        ativo_close = pd.to_numeric(ativo_close, errors='coerce')
        ativo_close.dropna(inplace=True)

        if ativo_close.empty:
            print(f"ERRO: Dados de fechamento inválidos para {ticker} após limpeza.")
            continue

        retorno_diario = ativo_close.pct_change().dropna() * 100
        
        if len(retorno_diario) < (janela_media_retorno + janela_prev + 5): # Checagem mínima de dados
             print(f"ERRO: Dados insuficientes para {ticker} (Pregões: {len(retorno_diario)}). Pulando.")
             continue
             
        print(f"Dados baixados com sucesso. Total de {len(retorno_diario)} pregões.")

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o download ou processamento de {ticker}: {e}")
        continue # Pula para o próximo ticker

    # --- 2. Preparação das Variáveis e Modelos ---
    
    # --- Modelo para o RETORNO MÉDIO ---
    retorno_medio_ativo = retorno_diario.rolling(window=janela_media_retorno).mean().dropna()
    df_retorno_medio = pd.DataFrame(retorno_medio_ativo)
    df_retorno_medio.columns = ['Alvo']
    for i in range(1, janela_prev + 1):
        df_retorno_medio[f'Lag_{i}'] = df_retorno_medio['Alvo'].shift(i)
    df_retorno_medio.dropna(inplace=True)

    if df_retorno_medio.empty:
        print(f"ERRO: Não foi possível criar o DF de lags de retorno para {ticker}. Pulando.")
        continue

    y_retorno_medio = df_retorno_medio['Alvo']
    X_retorno_medio = sm.add_constant(df_retorno_medio.drop('Alvo', axis=1))
    colunas_modelo_retorno = X_retorno_medio.columns
    modelo_retorno_medio = sm.OLS(y_retorno_medio, X_retorno_medio).fit()
    previsoes_retorno_historico = modelo_retorno_medio.predict(X_retorno_medio)

    # --- Modelo para a VOLATILIDADE ---
    volatilidade_ativo = retorno_diario.rolling(window=janela_vol).std().dropna()
    df_vol = pd.DataFrame(volatilidade_ativo)
    df_vol.columns = ['Alvo']
    for i in range(1, janela_prev + 1):
        df_vol[f'Lag_{i}'] = df_vol['Alvo'].shift(i)
    df_vol.dropna(inplace=True)

    if df_vol.empty:
        print(f"ERRO: Não foi possível criar o DF de lags de volatilidade para {ticker}. Pulando.")
        continue

    y_vol = df_vol['Alvo']
    X_vol = sm.add_constant(df_vol.drop('Alvo', axis=1))
    colunas_modelo_vol = X_vol.columns
    modelo_volatilidade = sm.OLS(y_vol, X_vol).fit()
    previsoes_vol_historico = modelo_volatilidade.predict(X_vol)


    # --- 3. Previsão para os Próximos 6 Meses ---
    # Calcula a data de início e fim da previsão (6 meses no futuro)
    data_inicio_previsao = y_retorno_medio.index[-1] + pd.Timedelta(days=1)
    data_final_previsao = data_inicio_previsao + pd.DateOffset(months=6)
    data_final_formatada = data_final_previsao.strftime('%b/%Y') # Para o gráfico
    
    datas_previsao = pd.bdate_range(start=data_inicio_previsao, end=data_final_previsao)


    # --- Previsão para Retorno Médio ---
    historico_retorno_medio = list(y_retorno_medio.values)
    previsoes_retorno_futuro = []
    print(f"Iniciando previsão de retorno médio para {ticker}...")
    for _ in datas_previsao:
        lags_values = [1] + historico_retorno_medio[-janela_prev:]
        df_previsao = pd.DataFrame([lags_values], columns=colunas_modelo_retorno)
        previsao = modelo_retorno_medio.predict(df_previsao).iloc[0].item()
        previsoes_retorno_futuro.append(previsao)
        historico_retorno_medio.append(previsao)

    # --- Previsão para Volatilidade ---
    historico_vol = list(y_vol.values)
    previsoes_vol_futura = []
    print(f"Iniciando previsão de volatilidade para {ticker}...")
    for _ in datas_previsao:
        lags_values_vol = [1] + historico_vol[-janela_prev:]
        df_previsao_vol = pd.DataFrame([lags_values_vol], columns=colunas_modelo_vol)
        previsao_vol = modelo_volatilidade.predict(df_previsao_vol).iloc[0].item()
        previsao_final_vol = max(0, previsao_vol) # Garante que vol não seja negativa
        previsoes_vol_futura.append(previsao_final_vol)
        historico_vol.append(previsao_final_vol)


    # --- 4. Cálculo para os Próximos 42 Dias ---
    retorno_esperado_42d = np.nan
    volatilidade_esperada_42d = np.nan
    
    if len(previsoes_retorno_futuro) >= 42 and len(previsoes_vol_futura) >= 42:
        retorno_previsto_42d = previsoes_retorno_futuro[:42]
        vol_prevista_42d = previsoes_vol_futura[:42]

        retorno_esperado_42d = np.mean(retorno_previsto_42d)
        volatilidade_esperada_42d = np.mean(vol_prevista_42d)
        
        print(f"\n--- Análise {ticker} (Próximos 42 Dias) ---")
        print(f"Retorno Médio Esperado: {retorno_esperado_42d:.4f}%")
        print(f"Volatilidade Média Esperada: {volatilidade_esperada_42d:.4f}")

    else:
        print(f"Não há dados de previsão suficientes para {ticker} (42 dias).")

    # Adiciona ao resultado final
    resultados_finais.append({
        'Ticker': ticker,
        'Retorno_Medio_42d': retorno_esperado_42d,
        'Volatilidade_Media_42d': volatilidade_esperada_42d
    })

    # --- 5. Visualização dos Resultados ---
    sns.set_style('darkgrid')
    plt.figure(figsize=(18, 12))

    # Gráfico para Retorno Médio
    plt.subplot(2, 1, 1)
    y_retorno_medio.plot(label=f'Retorno Médio Real ({janela_media_retorno}d)', color='blue', alpha=0.7)
    previsoes_retorno_historico.plot(label='Previsão Ajustada (Histórico)', color='violet', linestyle='--', alpha=0.9)
    serie_previsoes_retorno_futuro = pd.Series(previsoes_retorno_futuro, index=datas_previsao)
    
    # Atualiza o label do gráfico para refletir a data dinâmica
    serie_previsoes_retorno_futuro.plot(label=f'Previsão Futura (Até {data_final_formatada})', color='purple', linestyle='--')
    plt.title(f'Previsão do Retorno Médio Móvel de {janela_media_retorno} dias - {ticker}', fontsize=16)
    plt.ylabel('Retorno Médio Diário (%)')
    plt.axvline(y_retorno_medio.index[-1], color='black', linestyle='--', label='Início da Previsão Futura')
    plt.legend()
    plt.grid(True)

    # Gráfico para Volatilidade
    plt.subplot(2, 1, 2)
    y_vol.plot(label=f'Volatilidade Real ({janela_vol}d)', color='blue', alpha=0.7)
    previsoes_vol_historico.plot(label='Previsão Ajustada (Histórico)', color='violet', linestyle='--', alpha=0.9)
    serie_previsoes_vol_futura = pd.Series(previsoes_vol_futura, index=datas_previsao)
    
    # Atualiza o label do gráfico para refletir a data dinâmica
    serie_previsoes_vol_futura.plot(label=f'Previsão Futura (Até {data_final_formatada})', color='purple', linestyle='--')
    plt.title(f'Previsão da Volatilidade Móvel de {janela_vol} dias - {ticker}', fontsize=16)
    plt.ylabel('Desvio Padrão dos Retornos')
    plt.axvline(y_vol.index[-1], color='black', linestyle='--', label='Início da Previsão Futura')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    
    # Atualiza o nome do arquivo salvo
    nome_arquivo = f'previsao_media_movel_{ticker}_6meses.png'
    plt.savefig(nome_arquivo)
    print(f"Gráfico salvo como '{nome_arquivo}'")
    plt.close() # Fecha a figura para economizar memória no loop

# --- FIM DO LOOP ---

# --- 6. Exibição do Resumo Comparativo ---
print("\n\n=============================================================")
print(f"RESUMO DAS PREVISÕES (Próximos 42 dias)")
print("=============================================================")

if resultados_finais:
    df_resultados = pd.DataFrame(resultados_finais)
    df_resultados.set_index('Ticker', inplace=True)
    
    df_resultados['Retorno_Vol_Ratio'] = df_resultados['Retorno_Medio_42d'] / df_resultados['Volatilidade_Media_42d']
    df_resultados.sort_values(by='Retorno_Vol_Ratio', ascending=False, inplace=True)
    
    pd.set_option('display.precision', 4)
    print(df_resultados) 

    # --- 7. SALVAR DADOS PARA O SCRIPT DE CARTEIRA --- ### <<< ADICIONE ISSO ###
    nome_arquivo_saida = 'previsoes_finais.csv'
    try:
        df_resultados.to_csv(nome_arquivo_saida)
        print(f"\n[SUCESSO] Previsões salvas em '{nome_arquivo_saida}' para o script de carteira.")
    except Exception as e:
        print(f"\n[ERRO] Não foi possível salvar o arquivo CSV: {e}")
    ### <<< FIM DA ADIÇÃO ###

else:
    print("Nenhum resultado foi processado com sucesso.")