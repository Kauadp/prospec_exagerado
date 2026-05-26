import streamlit as st
from backend.scrapping import InstagramProspector

# Mapeamento Geográfico
MAPA_REGIOES = {
    "Rio de Janeiro (RJ)": {
        "hashtag_sufixo": "rj",
        "termos_bio": ["rj", "rio", "021", "caxias", "nova iguaçu", "sg", "niteroi", "copacabana"]
    },
    "São Paulo (SP)": {
        "hashtag_sufixo": "sp",
        "termos_bio": ["sp", "são paulo", "sampa", "011", "brás", "bom retiro", "itaim", "paulista"]
    }
}

# Mapeamento de Nicho
MAPA_SEGMENTOS = {
    "Moda & Vestuário": {
        "hashtag_prefixo": "moda",
        "termos_bio": ["moda", "loja", "boutique", "looks", "vestido", "t-shirt", "roupa", "clothing", "brand", "style", "alfaiataria", "jeans", "tshirt"]
    },
    "Sapatos": {
        "hashtag_prefixo": "sapatos",
        "termos_bio": ["sapatos", "calcados", "botas", "tenis", "sandalias", "scarpin", "flat", "rasteirinha", "salto", "shoes", "mocassim"]
    },
    "Joias & Semijoias": {
        "hashtag_prefixo": "joias",
        "termos_bio": ["joias", "semijoias", "prata", "prata925", "acessorios", "aneis", "brincos", "colares", "folheados", "banhado", "ouro"]
    },
    "Acessórios": {
        "hashtag_prefixo": "acessorios",
        "termos_bio": ["bag", "bolsas", "chapeu", "cinto", "oculos", "sunglasses", "carteiras", "mochilas", "boné", "lenço"]
    },
    "Moda Fitness": {
        "hashtag_prefixo": "fitness",
        "termos_bio": ["fitness", "gym", "academia", "treino", "legging", "top", "activewear", "esportivo", "crossfit", "maromba", "suplementos"]
    },
    "Produtos de Beleza": {
        "hashtag_prefixo": "beleza",
        "termos_bio": ["beleza", "cosmeticos", "maquiagem", "makeup", "skincare", "cabelo", "perfume", "estetica", "unhas", "batom", "skin", "gloss"]
    },
    "Eletrodomésticos": {
        "hashtag_prefixo": "eletro",
        "termos_bio": ["eletro", "eletrodomesticos", "casa", "cozinha", "geladeira", "fogao", "airfryer", "microondas", "tv", "tecnologia", "utilidades"]
    }
}

if "robo" not in st.session_state:
    st.session_state.robo = InstagramProspector("blablablaexg", "exagerado")

st.title("🎯 Gerador de Leads - Prospecção Comercial")

st.markdown("---")

# 1. Inputs amigáveis para a vendedora
regiao_selecionada = st.selectbox("Selecione o Estado/Região alvo:", list(MAPA_REGIOES.keys()))
segmento_selecionado = st.selectbox("Selecione o Segmento de Mercado:", list(MAPA_SEGMENTOS.keys()))
qtd_busca = st.slider("Quantidade de posts para analisar:", min_value=5, max_value=50, value=15)

# 2. O Pulo do Gato: Montagem automática dos parâmetros nos bastidores
dados_regiao = MAPA_REGIOES[regiao_selecionada]
dados_segmento = MAPA_SEGMENTOS[segmento_selecionado]

# Cria a hashtag dinamicamente (ex: moda + rj = modarj)
hashtag_automatica = f"{dados_segmento['hashtag_prefixo']}{dados_regiao['hashtag_sufixo']}"

# Une os termos de bio que o script vai varrer
termos_bio_localizacao = dados_regiao["termos_bio"]
termos_bio_segmento = dados_segmento["termos_bio"]

st.info(f"🔍 **Configuração de Busca Ativada:** Analisando a hashtag `#{hashtag_automatica}`")

# 3. Botão de disparo
if st.button("🚀 Iniciar Busca Inteligente"):
    with st.spinner("O robô está trabalhando... Isso pode levar alguns minutos para simular o comportamento humano."):
        
        leads = st.session_state.robo.buscar_leads(
            hashtag_alvo=hashtag_automatica,
            termos_localizacao=termos_bio_localizacao,
            termos_segmento=termos_bio_segmento,
            quantidade_posts=qtd_busca
        )
        
        if leads:
            st.success(f"Feito! Encontramos {len(leads)} leads qualificados!")
            import pandas as pd
            df = pd.DataFrame(leads)
            
            # Adiciona uma coluna de link clicável para o Instagram da loja
            df['link'] = df['username'].apply(lambda x: f"https://instagram.com/{x}")
            
            st.dataframe(df, column_config={
                "link": st.column_config.LinkColumn("Abrir Perfil 🔗")
            })
        else:
            st.warning("Nenhum lead passou nos critérios de filtro dessa vez. Tente aumentar a quantidade de posts analisados.")