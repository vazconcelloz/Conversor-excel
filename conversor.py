import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Importação de Segurados de Vida", layout="wide")
st.title("IMPORTAÇÕES DE SEGURADOS DE VIDA")

# Upload da planilha
arquivo = st.file_uploader("Envie sua planilha Excel", type=["xlsx"])

# Colunas que o sistema espera (fixas à esquerda)
colunas_arquivo = [
    "CONTRATO", "NÚMERO DA SUB", "NOME", "CPF", "NASCIMENTO",
    "Salário", "Cargo", "Data de admissão", "SEXO", "Estado civil",
    "Telefone", "E-mail", "CEP", "Endereço", "Número", "Bairro",
    "Cidade", "UF", "Agrupamento de cargos"
]

# ---- Funções de validação ----
def validar_cpf(cpf):
    cpf = re.sub(r"\D", "", str(cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return "INVÁLIDO"
    
    def calc_dv(cpf, digito):
        soma = sum(int(cpf[i]) * (digito - i) for i in range(digito-1))
        resto = (soma * 10) % 11
        return 0 if resto == 10 else resto

    if calc_dv(cpf, 10) != int(cpf[9]) or calc_dv(cpf, 11) != int(cpf[10]):
        return "INVÁLIDO"
    
    return cpf

def validar_data(data):
    try:
        return pd.to_datetime(data, dayfirst=True).strftime("%d/%m/%Y")
    except:
        return "INVÁLIDO"

def validar_salario(sal):
    try:
        return float(str(sal).replace(",", "."))
    except:
        return 0.0

def validar_telefone(tel):
    tel = re.sub(r"\D", "", str(tel))
    if len(tel) == 11:
        return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
    elif len(tel) == 10:
        return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
    return "INVÁLIDO"

def validar_uf(uf):
    uf = str(uf).upper()
    return uf if len(uf) == 2 else "INVÁLIDO"

# Função para estilizar células inválidas
def highlight_invalid(val):
    if val == "INVÁLIDO":
        return 'background-color: #FFCCCC'  # vermelho claro
    return ''

if arquivo:
    df = pd.read_excel(arquivo)
    st.write("Pré-visualização da planilha enviada:")
    st.dataframe(df.head())

    st.subheader("Mapeamento de Colunas")
    col1, col2 = st.columns([1, 2])

    mapeamento = {}
    with col1:
        st.markdown("**COLUNA DO ARQUIVO ENVIADO**")
        for col in colunas_arquivo:
            st.write(col)

    with col2:
        st.markdown("**COLUNA CORRESPONDENTE**")
        for col in colunas_arquivo:
            escolha = st.selectbox(
                f"Selecione a coluna para '{col}':",
                [""] + list(df.columns),
                key=col
            )
            mapeamento[col] = escolha

    st.subheader("Nome do arquivo de saída")
    nome_arquivo = st.text_input("Digite o nome do arquivo (sem extensão)", value="saida_validada")

    if st.button("Avançar"):
        novo_df = pd.DataFrame()
        for col_final, col_original in mapeamento.items():
            if col_original and col_original in df.columns:
                novo_df[col_final] = df[col_original]
            else:
                novo_df[col_final] = ""

        # ---- Aplicando validações ----
        if "CPF" in novo_df:
            novo_df["CPF"] = novo_df["CPF"].apply(validar_cpf)
        if "NASCIMENTO" in novo_df:
            novo_df["NASCIMENTO"] = novo_df["NASCIMENTO"].apply(validar_data)
        if "Data de admissão" in novo_df:
            novo_df["Data de admissão"] = novo_df["Data de admissão"].apply(validar_data)
        if "Salário" in novo_df:
            novo_df["Salário"] = novo_df["Salário"].apply(validar_salario)
        if "Telefone" in novo_df:
            novo_df["Telefone"] = novo_df["Telefone"].apply(validar_telefone)
        if "UF" in novo_df:
            novo_df["UF"] = novo_df["UF"].apply(validar_uf)

        st.success("Transformação concluída com validação!")

        # Mostrar DataFrame com células inválidas em vermelho
        st.dataframe(novo_df.style.applymap(highlight_invalid))

        # Contagem de registros inválidos
        total_invalidos = (novo_df == "INVÁLIDO").any(axis=1).sum()
        if total_invalidos > 0:
            st.warning(f"Foram detectadas {total_invalidos} linhas com dados inválidos.")

        # ---- Download em memória ----
        buffer = BytesIO()
        novo_df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Baixar planilha transformada",
            data=buffer,
            file_name=f"{nome_arquivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
