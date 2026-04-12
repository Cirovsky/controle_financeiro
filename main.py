import streamlit as st
import pandas as pd
import numpy as np
from misc_func import localiza_data_proxima

def revela_valor(valor):
    print(f"aqui:{valor[-1]}\nfim")
    return 1

def calc_stats(df:pd.DataFrame):
    df = df.groupby(by="Data")[["Valor"]].sum()
    df["Data"] = df.index.to_list()
    df["Diferenca_Mensal"] = df["Valor"] - df["Valor"].shift(1)
    df["Avg_6M_Diferenca"] = df["Diferenca_Mensal"].rolling(6).mean()
    df["Avg_12M_Diferenca"] = df["Diferenca_Mensal"].rolling(12).mean()
    df["Avg_24M_Diferenca"] = df["Diferenca_Mensal"].rolling(24).mean()
    df["Diferenca_Rel_Mensal"] = df["Valor"] / df["Valor"].shift(1) -1
    df["Diferenca_Rel_Mensal(AGV_12M)"] = df["Diferenca_Rel_Mensal"].rolling(12).apply(lambda x: x.mean())
    df["Diferenca_Anual"] = df["Valor"].rolling(df.shape[0]).apply(lambda x: x[-1] - x[0], raw=True)
    df["Diferenca_Rel_Anual"] = df["Valor"].rolling(df.shape[0]).apply(lambda x: x[-1] / x[0] -1, raw=True)
    diferenca_datas:pd.Series = (df["Data"] - df["Data"].shift(1)).map(lambda dt: dt.days if dt is not np.nan else dt)
    df.drop(columns="Data",inplace=True)
    df["Ganho_Avg_Diario"] = df["Diferenca_Mensal"]/diferenca_datas.map(lambda dif: dif*(22/30))
    primeiro_valor_valido = df["Valor"].dropna().iloc[0]
    print(primeiro_valor_valido)
    df["Diferenca_Acumulada"] = df["Valor"].map(lambda x: x - primeiro_valor_valido)
    df["Diferenca_Acumulada_Rel"] = df["Valor"].map(lambda x: x / primeiro_valor_valido -1)
    return df
st.set_page_config(page_title="Finanças",page_icon=":moneybag:")
st.markdown("""
    # Boas Vindas!
    ## Nosso app financeiro!
""")
st.html("""
    <div>testando HTML</div>
""")

#Widget de upload de dados
file_upload = st.file_uploader("Faça upload dos dados", type=['csv'])

#verifica se foi feito upload
if file_upload:
    #leitura dos dados
    df:pd.DataFrame = pd.read_csv(file_upload)
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y").dt.date
    column_fmt = {"Valor": st.column_config.NumberColumn("Valor",format="R$ %f")}

    #exibição dos dados no App
    exp1 = st.expander("Dados Brutos")
    exp1.dataframe(df, hide_index=True, column_config=column_fmt)
    
    #Visão Instituição
    exp2 = st.expander("Instituições")
    df_instituicao:pd.DataFrame = df.pivot_table(index="Data", columns="Instituição", values="Valor")
    tab_data, tab_history, tab_share = exp2.tabs(["Dados", "Histórico", "Distribuição"])
    
    with tab_data:
        st.dataframe(df_instituicao)
    with tab_history:
        st.line_chart(df_instituicao)
    with tab_share:
        date = st.date_input(label="Selecione data"
                      , min_value=df_instituicao.index.min()
                      ,max_value=df_instituicao.index.max())
        if date not in df_instituicao.index:
            date = localiza_data_proxima(df_instituicao,date)
            st.html(f"<div style='height: 20px; color: orange'>exibindo resultado de: {date}</div>")
            st.bar_chart(df_instituicao.loc[date])
        else:
            st.html(f"<div style='height: 20px'> </div>")
            last_dt = df_instituicao.sort_index().iloc[-1]
            st.bar_chart(df_instituicao.loc[date])
    
    exp3 = st.expander("Estatisticas Gerais")
    df_stats = calc_stats(df)
    columns_config ={ col:st.column_config.NumberColumn(col, format="R$ %.2f") if not col.__contains__("Rel") else st.column_config.NumberColumn(col, format="percent") for col in df_stats.columns.to_list()}
    tab_data_eg, tab_hist_patrimonio, tab_hist_diff, tab_hist_acc = exp3.tabs(["Dados", "Patrimônio", "Diferença", "Acumulado"])
    with tab_data_eg:
        st.dataframe(df_stats,column_config=columns_config)
    with tab_hist_patrimonio:
        st.line_chart(df_stats["Valor"])
    with tab_hist_diff:
        st.line_chart(df_stats[["Diferenca_Mensal","Avg_6M_Diferenca","Avg_12M_Diferenca", "Diferenca_Anual"]])
    cols_abs = [col for col in df_stats.columns.to_list() if not col.__contains__("Rel")]
    with tab_hist_acc:
        st.line_chart(df_stats["Diferenca_Acumulada"])
    cols_abs = [col for col in df_stats.columns.to_list() if not col.__contains__("Rel")]

#não tem arquivos