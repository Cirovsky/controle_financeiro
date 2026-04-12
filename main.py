import streamlit as st
import pandas as pd
from misc_func import localiza_data_proxima

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
            st.html(f"<div>exibindo resultado de: {date}</div>")
            st.bar_chart(df_instituicao.loc[date])
        else: 
            last_dt = df_instituicao.sort_index().iloc[-1]
            st.bar_chart(df_instituicao.loc[date])

    #st.dataframe=(df_instituicao)
#não tem arquivos