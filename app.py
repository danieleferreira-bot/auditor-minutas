import streamlit as st
import requests
import docx
import difflib
import google.generativeai as genai
import pypdf

# --- FUNÇÃO: LER ARQUIVOS DO WORD ---
def extrair_texto_docx(arquivo):
    doc = docx.Document(arquivo)
    texto = []
    for paragrafo in doc.paragraphs:
        if paragrafo.text.strip(): 
            texto.append(paragrafo.text)
    return texto

# --- FUNÇÃO: LER ARQUIVOS PDF ---
def extrair_texto_pdf(arquivo):
    leitor_pdf = pypdf.PdfReader(arquivo)
    texto = []
    for pagina in leitor_pdf.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            linhas = texto_pagina.split('\n')
            for linha in linhas:
                if linha.strip():
                    texto.append(linha)
    return texto

# --- FUNÇÃO INTELIGENTE: ESCOLHE O LEITOR CERTO ---
def extrair_texto(arquivo):
    if arquivo.name.lower().endswith('.pdf'):
        return extrair_texto_pdf(arquivo)
    elif arquivo.name.lower().endswith('.docx'):
        return extrair_texto_docx(arquivo)
    else:
        return []

# Configuração da Página
st.set_page_config(page_title="Auditor de Minutas", page_icon="🕵️‍♂️", layout="wide")
st.title("Auditor de Minutas 🕵️‍♂️")
st.write("Automatize a conferência e revisão dos seus contratos em Word ou PDF.")

# --- ABAS DO SISTEMA ---
aba1, aba2, aba3 = st.tabs(["🔍 Comparar Minutas", "🧠 Revisor com IA", "🏢 Consultar CNPJ"])

# ==========================================
# ABA 1: COMPARADOR DE MINUTAS
# ==========================================
with aba1:
    st.subheader("Comparativo de Alterações de Texto")
    minuta_antiga = st.file_uploader("Anexe a Minuta Antiga", type=["docx", "pdf"], key="antiga")
    minuta_nova = st.file_uploader("Anexe a Minuta Nova", type=["docx", "pdf"], key="nova")

    if minuta_antiga and minuta_nova:
        if st.button("Comparar Textos"):
            texto_antigo = extrair_texto(minuta_antiga)
            texto_novo = extrair_texto(minuta_nova)
            diferencas = list(difflib.ndiff(texto_antigo, texto_novo))
            
            mudancas_encontradas = False
            for linha in diferencas:
                if linha.startswith("- "):
                    st.error(f"**Removido:** {linha[2:]}") 
                    mudancas_encontradas = True
                elif linha.startswith("+ "):
                    st.success(f"**Adicionado/Alterado:** {linha[2:]}") 
                    mudancas_encontradas = True
                    
            if not mudancas_encontradas:
                st.info("Nenhuma diferença de texto foi encontrada!")

# ==========================================
# ABA 2: REVISOR INTELIGENTE COM GEMINI
# ==========================================
with aba2:
    st.subheader("Revisor Jurídico Avançado")
    st.write("Nossa IA fará uma varredura buscando erros de português, concordância de gênero, dados geográficos e pontuação.")
    
    chave_api = st.text_input("Cole sua Chave de API do Google Gemini:", type="password")
    documento_revisao = st.file_uploader("Anexe o documento que deseja revisar", type=["docx", "pdf"], key="revisao")
    
    if st.button("Iniciar Revisão Profunda"):
        if not chave_api:
            st.warning("⚠️ Por favor, cole a sua Chave de API do Gemini no campo acima.")
        elif documento_revisao is None:
            st.warning("⚠️ Por favor, anexe um documento.")
        else:
            with st.spinner("A IA está lendo e revisando o documento. Isso pode levar alguns segundos..."):
                try:
                    genai.configure(api_key=chave_api)
                    
                    # Usando o modelo universal e mais estável
                    modelo = genai.GenerativeModel('gemini-pro')
                    
                    texto_completo = "\n".join(extrair_texto(documento_revisao))
                    
                    comando_prompt = f"""
                    Atue como um revisor de textos e documentos profissionais, jurídicos e contratuais, com foco em precisão gramatical, concordância nominal e lógica.

                    TAREFA: Analise o documento enviado e identifique erros seguindo estes critérios rigorosos:
                    1. Dados Gerais: Verifique a coerência de datas, e verifique a coerência entre os estados e municípios informados no documento.
                    2. Erros de Digitação: Identifique palavras grafadas incorretamente ou letras trocadas.
                    3. Identificação e Correção de Gênero: Analise o nome próprio do sujeito principal para identificar se é homem ou mulher. Identificado o gênero do nome, aponte e corrija todas as palavras no texto (pronomes, adjetivos, profissões) que estiverem no gênero oposto ou misturadas.
                    4. Pontuação: Verifique o uso de vírgulas, pontos finais e coerência nos parágrafos.

                    FORMATO FINAL:
                    Apresente os erros encontrados em uma lista contendo: "Trecho Original" | "Sugestão de Correção". 
                    Ao final, forneça o texto completo e revisado.

                    DOCUMENTO A SER REVISADO:
                    {texto_completo}
                    """
                    
                    resposta_ia = modelo.generate_content(comando_prompt)
                    
                    st.success("Revisão Concluída!")
                    st.write(resposta_ia.text)
                    
                except Exception as e:
                    st.error(f"Ocorreu um erro ao conectar com a IA. Erro técnico: {e}")

# ==========================================
# ABA 3: INTEGRAÇÃO RECEITA FEDERAL
# ==========================================
with aba3:
    st.subheader("Integração com a Receita Federal")
    cnpj_teste = st.text_input("Digite um CNPJ (só números):")

    if st.button("Consultar CNPJ"):
        if cnpj_teste:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_teste}"
            resposta = requests.get(url)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                st.success("Dados encontrados com sucesso!")
                st.write(f"**Razão Social:** {dados.get('razao_social')}")
                st.write(f"**Endereço:** {dados.get('logradouro')}, {dados.get('numero')} - {dados.get('municipio')}/{dados.get('uf')}")
            else:
                st.error("CNPJ não encontrado.")
