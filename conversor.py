import streamlit as st
import pandas as pd
from enum import Enum


# -------------------------------
# Enum para tipos de colunas
# -------------------------------
class TipoColuna(Enum):
    OBRIGATORIA = "obrigatória"
    CONDICIONAL = "condicional"
    FACULTATIVA = "facultativa"


# -------------------------------
# Estrutura dos formatos
# -------------------------------
formatos = {
    "vida": {
        "titulo": "IMPORTAÇÕES DE VIDA",
        "obrigatorias": ["CPF", "Nome", "Nascimento", "Sexo", "Inclusão"],
        "condicionais": ["Carteirinha", "Código Plano", "Acomodação"],
        "facultativas": ["Telefone", "E-mail", "Endereço", "Cargo"]
    },
    "saude": {
        "titulo": "IMPORTAÇÕES DE SAÚDE",
        "obrigatorias": [
            "CPF", "Parentesco", "Nome", "Nascimento", "Sexo",
            "Estado civil", "Nome da mãe", "Inclusão", "Envio", "Entrada"
        ],
        "condicionais": [
            "CPF Titular", "Código/Nome Unidade", "Código Centro Custo",
            "Centro de custo", "Código/Nome unidade de atendimento",
            "Código Plano", "Plano", "Acomodação", "Id do tipo de comissão",
            "Grupo", "Seq. Grupo", "Carteirinha", "End. Res. CEP",
            "End. Res. Logradouro", "End. Res. Bairro", "End. Res. Cidade",
            "End. Res. UF", "Tel. Res. DDD", "Tel. Res.", "Tel. Com. DDD",
            "Tel. Com.", "Tel. Cel. DDD", "Tel. Cel.", "Banco", "Agência",
            "Dígito da Agência", "Conta"
        ],
        "facultativas": [
            "Contrato","Agregado","Altura","Peso","Nome do Pai","Cargo","RE",
            "Admissão","Código/Nome Unidade","Conclusão","Previsão Carteirinha",
            "Chegada Carteirinha","Envio Carteirinha","Vencimento Carteirinha",
            "Código do usuário na Cia.","Limite de reembolso","RG","RG emissão",
            "Órgão emissor","PIS","CNS","CTPS","CTPS Emis.","Nascido Vivo",
            "End. Res. Nº","End. Res. Comp","Tel. Res. Comp.","Tel. Com. Comp.",
            "Tel. Cel. Comp.","E-mail pessoal","E-mail comercial"
        ]
    }
}


# -------------------------------
# Função para gerar lista de colunas
# -------------------------------
def gerar_colunas(formato: str):
    colunas = []
    for nome in formatos[formato]["obrigatorias"]:
        colunas.append({"nome": nome, "tipo": TipoColuna.OBRIGATORIA.value})
    for nome in formatos[formato]["condicionais"]:
        colunas.append({"nome": nome, "tipo": TipoColuna.CONDICIONAL.value})
    for nome in formatos[formato]["facultativas"]:
        colunas.append({"nome": nome, "tipo": TipoColuna.FACULTATIVA.value})
    return colunas


# -------------------------------
# Função para validar obrigatórias
# -------------------------------
def validar_obrigatorias(df, obrigatorias):
    erros = []
    for col in obrigatorias:
        if col not in df.columns:
            erros.append(f"Coluna obrigatória '{col}' não encontrada no arquivo.")
        elif df[col].isnull().any():
            erros.append(f"Coluna obrigatória '{col}' contém valores nulos.")
    return erros


# -------------------------------
# App Streamlit
# -------------------------------
st.title("Validador de Importações")

# Escolha do formato
formato_escolhido = st.selectbox(
    "Selecione o tipo de importação",
    list(formatos.keys()),
    format_func=lambda x: formatos[x]["titulo"]
)

st.subheader("Colunas esperadas")

# Exibir tabela de colunas com ícones
cores = {"obrigatória": "🔴", "condicional": "🔵", "facultativa": "🟢"}
colunas_formatadas = [
    {"Coluna": col["nome"], "Tipo": cores[col["tipo"]]}
    for col in gerar_colunas(formato_escolhido)
]
st.table(pd.DataFrame(colunas_formatadas))

# Upload do arquivo Excel
arquivo = st.file_uploader("Envie o arquivo Excel", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)
    st.subheader("Prévia dos dados")
    st.dataframe(df.head())

    erros = validar_obrigatorias(df, formatos[formato_escolhido]["obrigatorias"])

    st.subheader("Validação")
    if erros:
        st.error("Foram encontrados erros:")
        for e in erros:
            st.write(f"- {e}")
    else:
        st.success("Arquivo válido para importação!")
