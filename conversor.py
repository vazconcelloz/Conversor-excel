import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Conversor de Segurados", layout="wide")

# -------------------------------
# Estrutura dos formatos
# -------------------------------
formatos = {
    "vida": {
        "titulo": "IMPORTAÇÕES DE SEGURADOS DE VIDA",
        "obrigatorias": ["CONTRATO", "NÚMERO DA SUB", "NOME", "CPF", "NASCIMENTO"],
        "condicionais": ["Salário", "Cargo", "Data de admissão", "SEXO", "Estado civil", "Telefone", "E-mail", "UF", "Agrupamento de cargos"],
        "facultativas": []
    },
    "saude": {
        "titulo": "IMPORTAÇÕES DE SEGURADOS DE SAÚDE",
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
            "Erros", "Contrato", "Numero da sub", "Agregado", "Altura", "Peso",
            "Nome do Pai", "Cargo", "RE", "Admissão", "Conclusão",
            "Previsão Carteirinha", "Chegada Carteirinha", "Envio Carteirinha",
            "Vencimento Carteirinha", "Código do usuário na Cia.", "Limite de reembolso",
            "RG", "RG emissão", "Órgão emissor", "PIS", "CNS", "CTPS", "CTPS Emis.",
            "Nascido Vivo", "End. Res. Nº", "End. Res. Comp", "Tel. Res. Comp.",
            "Tel. Com. Comp.", "Tel. Cel. Comp.", "E-mail pessoal", "E-mail comercial"
        ]
    }
}

# -------------------------------
# Funções de validação originais
# -------------------------------
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

def highlight_invalid(val):
    if val == "INVÁLIDO":
        return 'background-color: #FFCCCC'
    return ''

# -------------------------------
# Interface Streamlit
# -------------------------------
st.title("Conversor de Segurados")

# Escolha do formato
formato_escolhido = st.selectbox(
    "Selecione o tipo de importação",
    list(formatos.keys()),
    format_func=lambda x: formatos[x]["titulo"]
)

colunas_config = []
for tipo in ["obrigatorias", "condicionais", "facultativas"]:
    for col in formatos[formato_escolhido][tipo]:
        colunas_config.append({"nome": col, "tipo": tipo})

# Mostrar tabela de colunas com cores
cores = {"obrigatorias": "🔴", "condicionais": "🔵", "facultativas": "🟢"}
st.subheader("Colunas esperadas")
st.table(pd.DataFrame([{"Coluna": c["nome"], "Tipo": cores[c["tipo"]]} for c in colunas_config]))

# Upload da planilha
arquivo = st.file_uploader("Envie sua planilha Excel", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)
    st.subheader("Pré-visualização da planilha")
    st.dataframe(df.head())

    st.subheader("Mapeamento de Colunas")
    col1, col2 = st.columns([1, 2])
    mapeamento = {}
    with col1:
        st.markdown("**Coluna esperada**")
        for c in colunas_config:
            st.write(f"{cores[c['tipo']]} {c['nome']}")
    with col2:
        st.markdown("**Coluna correspondente no arquivo**")
        for c in colunas_config:
            escolha = st.selectbox(
                f"{c['nome']} ({c['tipo']})",
                [""] + list(df.columns),
                key=c['nome']
            )
            mapeamento[c['nome']] = escolha

    st.subheader("Nome do arquivo de saída")
    nome_arquivo = st.text_input("Digite o nome do arquivo (sem extensão)", value="saida_validada")

    if st.button("Converter"):
        # Montar novo DataFrame
        novo_df = pd.DataFrame()
        for col_final, col_original in mapeamento.items():
            if col_original and col_original in df.columns:
                novo_df[col_final] = df[col_original]
            else:
                novo_df[col_final] = ""

        # Aplicar validações específicas
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

        st.success("Conversão concluída!")

        # Mostrar DataFrame com células inválidas em vermelho
        st.dataframe(novo_df.style.applymap(highlight_invalid))

        # --- Preparar arquivo para download ---
        download_df = novo_df.copy()
        
        # Adicionar coluna "ERRO" como primeira coluna para saúde
        if formato_escolhido == "saude":
            download_df.insert(0, "ERRO", "")

        buffer = BytesIO()
        download_df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Baixar planilha convertida",
            data=buffer,
            file_name=f"{nome_arquivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
