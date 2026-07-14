import streamlit as st
import requests
import docx
import difflib

# --- FUNÇÃO NOVA: LER ARQUIVOS DO WORD ---
def extrair_texto_docx(arquivo):
    doc = docx.Document(arquivo)
    texto = []
    for paragrafo in doc.paragraphs:
        # Pega apenas os parágrafos que têm algum texto (ignora espaços em branco)
        if paragrafo.text.strip(): 
            texto.append(paragrafo.text)
    return texto

# Título da sua página
st.title("Auditor de Minutas 🕵️‍♂️")
st.write("Faça o upload dos contratos e cruze com a Receita Federal.")

# Espaço para Upload dos arquivos
minuta_antiga = st.file_uploader("Anexe a Minuta Antiga", type=["docx"])
minuta_nova = st.file_uploader("Anexe a Minuta Nova", type=["docx"])

# --- NOVO BLOCO: O CÉREBRO DA COMPARAÇÃO ---
if minuta_antiga is not None and minuta_nova is not None:
    st.subheader("🔍 Comparativo de Alterações")
    
    if st.button("Comparar Minutas"):
        # 1. Lê o texto dos dois arquivos anexados
        texto_antigo = extrair_texto_docx(minuta_antiga)
        texto_novo = extrair_texto_docx(minuta_nova)
        
        # 2. Faz a comparação linha por linha
        diferencas = list(difflib.ndiff(texto_antigo, texto_novo))
        
        st.write("### Resultado da Análise:")
        
        mudancas_encontradas = False
        
        # 3. Pinta os resultados na tela
        for linha in diferencas:
            # Se a linha começa com '-', significa que foi APAGADA da minuta antiga
            if linha.startswith("- "):
                st.error(f"**Removido:** {linha[2:]}") 
                mudancas_encontradas = True
                
            # Se a linha começa com '+', significa que foi ADICIONADA na minuta nova
            elif linha.startswith("+ "):
                st.success(f"**Adicionado/Alterado:** {linha[2:]}") 
                mudancas_encontradas = True
                
        if not mudancas_encontradas:
            st.info("Nenhuma diferença de texto foi encontrada entre as duas minutas!")
        else:
            st.info("💡 As partes do texto que são idênticas nos dois arquivos foram ocultadas para focar apenas nas alterações.")

st.divider() # Uma linha para separar a tela

# Testando a busca de CNPJ
st.subheader("Teste de Integração com a Receita")
cnpj_teste = st.text_input("Digite um CNPJ para testar (só números):")

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
            st.error("CNPJ não encontrado ou erro na comunicação. A API pode estar instável no momento.")
            