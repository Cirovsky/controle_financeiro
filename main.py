import streamlit as st
import pandas as pd
import numpy as np
from misc_func import localiza_data_proxima

#retirar a função abaixo após finalizar o dashboard
def revela_valor(valor):
    """auxiliar quando tiver dúvidas sobre qual o retorno de alguma função anônima"""
    print(f"aqui:{valor[-1]}\nfim")
    return 1

def calc_stats(df:pd.DataFrame):
    """auxilia nos cálculas das estatísticas básicas, criando colunas para cada estatística"""
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

class botao_date:
    key = 0
    def __init__(self,df:pd.DataFrame):
        """para o uso desta classe, o dataframe deve ter index configurado com date/datetime"""
        self.min_value = df.index.min()
        self.max_value = df.index.max()
        botao_date.key+= 1
    def criar_botao(self):
        return st.date_input(label="Selecione data", min_value= self.min_value, max_value= self.max_value, key=botao_date.key)

st.set_page_config(page_title="Finanças",page_icon=":moneybag:")

#Widget de upload de dados
#file_upload = st.file_uploader("Faça upload dos dados", type=['csv'])
file_upload = "datasets/Template Controle Financeiro - Saldo Mensal.csv"

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
        date = botao_date(df_instituicao).criar_botao()
        #date = st.date_input(label="Selecione data", min_value=df_instituicao.index.min(),max_value=df_instituicao.index.max())
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
    tab_stats, tab_hist_patrimonio, tab_hist_diff, tab_hist_acc = exp3.tabs(["Dados", "Patrimônio", "Diferença", "Acumulado"])
    with tab_stats:
        st.dataframe(df_stats,column_config=columns_config)
    with tab_hist_patrimonio:
        st.line_chart(df_stats["Valor"])
    with tab_hist_diff:
        st.line_chart(df_stats[["Diferenca_Mensal","Avg_6M_Diferenca","Avg_12M_Diferenca", "Diferenca_Anual"]])
    with tab_hist_acc:
        st.line_chart(df_stats["Diferenca_Acumulada"])
    exp4 = st.expander("Metas")
    tab_rendimentos, tab_data_meta, tab_meta_rel, tab_meta_abs = exp4.tabs(["Data","rendimentos","meta_rel","meta_abs"])
    with tab_rendimentos:
        date2 = botao_date(df_instituicao).criar_botao()
        sal_bruto:float= (st.number_input(label="digite seu salário (em reais):",min_value=0, key='sal_bruto'))
        sal_liq:float= (st.number_input(label="digite seu salário (em reais):",min_value=0, key = "sal_liquido"))
        tax_seliq:float = (st.number_input(label="digite a taxa selic(em decimal):",min_value=0, max_value=1, key= "tax_seliq"))

#não tem arquivos'