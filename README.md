# 🚀 Motor de Prospecção Inteligente & Dashboard Comercial (Human-in-the-Loop)

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-ff4b4b?logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/Banco-PostgreSQL-336791?logo=postgresql)
![Status](https://img.shields.io/badge/Status-Production--Ready-green)

---

## 📋 Visão Geral

Este projeto é um sistema inteligente de **Inteligência de Mercado e Sales Ops** voltado para prospecção ativa de B2B regional. A aplicação substitui buscas manuais e ineficientes por um pipeline automatizado de extração geográfica combinada com Inteligência Artificial (NLP). 

O sistema minera leads reais diretamente da **Google Places API (New)**, filtra duplicados em tempo de execução para economizar cota, analisa semanticamente as avaliações dos clientes para extrair o sentimento e calcula um score de maturidade comercial (0 a 100). Por fim, os dados alimentam um dashboard executivo com funil de vendas e um laboratório científico para análise estatística e calibração de modelos.

---

## 📂 Estrutura do Projeto

├── backend/
│   ├── contracts/                # 📑 Pipeline de Automação de Contratos
│   │   ├── apis/
│   │   │   ├── autentique.py     # Integração com API de assinatura eletrônica
│   │   │   └── brasil_api.py     # Consulta automatizada de dados cadastrais de CNPJ
│   │   ├── config/
│   │   │   └── eventos.py        # Configurações logísticas de precificação dos eventos
│   │   ├── dados_evento/
│   │   │   └── rj.py             # Parâmetros e regras de negócio da operação Rio
│   │   ├── contract_services.py  # Lógica de preenchimento e geração de arquivos DOCX/PDF
│   │   └── get_data.py           # barramento de extração de insumos contratuais
│   ├── conector_google.py        # Wrapper de baixo nível para requisições no Google Places New
│   ├── db_repository.py          # Gerenciamento de conexões à infraestrutura Postgres (Supabase)
│   ├── prospector.py             # Orquestrador do motor de busca, NLP e Heurística de Score
│   └── queries.py                # Repositório de queries SQL otimizadas
├── contratos/                    # 📂 Output de contratos gerados (.docx e .pdf)
├── dash/                         # 🖥️ Camada Visual e Relatórios (Streamlit)
│   ├── app.py                    # Arquivo master da interface (Gerenciamento de Abas)
│   ├── db_dash.py                # Queries e conexões exclusivas de renderização do painel
│   ├── maps.py                   # Integração da esteira visual com o motor de prospecção
│   ├── services.py               # Funções de suporte e transformações de dados da UI
│   └── theme.py                  # Identidade visual, paleta de cores e componentes customizados
├── template/                     # 📝 Arquivos base do Word para fusão de dados (.docx)
│   ├── template_avista_comissionado_rj.docx
│   ├── template_avista_rj.docx
│   ├── template_parcelado_comissionado_rj.docx
│   └── template_parcelado_rj.docx
├── README.md                     # Documentação técnica unificada
└── requirements.txt              # Dependências de produção do projeto

---

## 🗄️ Arquitetura do Banco de Dados

A persistência é feita em uma instância PostgreSQL hospedada no Supabase. Para garantir a integridade analítica e evitar erros nos filtros temporais dos dashboards, a base de dados opera globalmente sincronizada no fuso horário de Brasília (**`America/Sao_Paulo`**).

### Tabela Principal: `leads_prospecção_inteligente`

* `id` (SERIAL PRIMARY KEY): Identificador único do registro.
* `nome_empresa` (VARCHAR): Nome fantasia do estabelecimento capturado.
* `segmento` (VARCHAR): Categoria comercial alvo da busca.
* `regiao_cidade` (VARCHAR): Cidade ou microrregião delimitada na varredura.
* `telefone` / `site` / `endereco_completo` (VARCHAR): Dados de contato enriquecidos.
* `place_id_google` (VARCHAR UNIQUE): ID único do estabelecimento no Google Maps. Atua como trava natural.
* `rating_maps` (NUMERIC) / `total_reviews` (INT): Métricas de reputação e volume físico.
* `sentimento_reviews_medio` (NUMERIC): Média semântica gerada pelo modelo NLP.
* `score_heuristico` (NUMERIC): Nota final de priorização comercial (0.00 a 100.00).
* `instagram` (VARCHAR): Identificador da rede social, preenchido na curadoria humana.
* `validado_por_humano` (BOOLEAN): Flag de qualificação comercial da esteira (*Human-in-the-Loop*).
* `criado_em` / `atualizado_em` (TIMESTAMP): Timestamps automatizados no fuso local.

---

## ⚙️ Engenharia e Motores Core

### 1. Motor de Prospecção Inteligente (`backend/prospector.py`)
O motor estende uma consulta padrão aplicando uma matriz de sinônimos regionalizada (`MAPA_SEGMENTOS`), permitindo que termos corporativos genéricos expandam em buscas granulares de fachadas de lojas reais.

* **Cache Preventivo de Custos:** Antes de despachar requisições complexas ou processar inteligência linguística, o robô faz uma verificação atômica de existência indexada por `place_id_google`. Se o lead já consta na base, ele executa um *Skip* instantâneo, poupando processamento e mantendo o teto estável de requisições de cotas de APIs.
* **Algoritmo de Score Comercial Avançado (0-100):** A priorização do lead não se baseia apenas no tamanho da empresa. Ela une dados de volume físico com análise semântica estruturada pelo dicionário **`LeIA`** (VADER adaptado para Português):
  $$\text{Score Base} = (\text{Rating} \times 8) + \min\left(\left(\frac{\text{Total Reviews}}{150}\right) \times 20, 30\right)$$
  O sentimento atua como um **modulador estratégico de vendas**:
  * **Lead Promotor ($>0.4$):** O público venera a marca. Recebe bônus proporcional de engajamento de até 30 pontos.
  * **Lead Detrator com Volume ($<-0.15$ e $>50$ reviews):** Empresa grande com problemas locais latentes. O algoritmo injeta até 25 pontos de bônus por **Urgência Comercial (Dor do Lead)** para abordagem focada em conversão.

### 2. Triagem Interativa e Curadoria (*Human-in-the-Loop*)
Desenvolvida para mitigar falhas de dados nulos (convertidos de `None` para `"Não Encontrado"` via Pandas), a interface renderiza uma tabela interativa protegida utilizando o `st.data_editor` do Streamlit.
O usuário clica nos sites gerados, realiza a avaliação estética/visual da marca, insere o `@instagram` diretamente na célula e carimba o selo **Qualificado?** via checkbox, disparando um `UPDATE` limpo e atômico no Postgres por meio do método:
```python
db_manager.atualizar_curadoria_lead(lead_id, is_validado, insta_handle)
```

## 📊 Estrutura e Abas do Dashboard (dash/app.py)

A interface gráfica foi particionada de forma lógica para atender a duas frentes distintas da operação:

### Seção 1: Painel Executivo (Foco: Gerência)

 - Visão de Metas e Períodos: Filtros dinâmicos ("Hoje", "Esta Semana", "Este Mês") integrados de forma nativa e precisa com as datas do banco.

 - Funil Volumétrico Comercial (Plotly): Desenha graficamente as etapas da esteira de vendas (Agendado → Reunião Realizada → Tô Dentro → Contrato Enviado → Contrato Assinado).

 - Ranking de Agendadoras: Tabela consolidada com taxas de conversão individualizadas, eficiência de fechamento e atingimento de metas.

### Seção 2: Laboratório Científico de Sales Ops (Foco: Estudo de Dados)

Desenvolvida para expor métricas preditivas, gerando gatilhos visuais imediatos para intervenções ou estudos profundos via Jupyter Notebooks:

 - Gráfico de Calibração do Modelo: Avalia a média do Score (0-100) contra a decisão humana (Aprovado vs. Rejeitado). Se a média dos aprovados não for drasticamente superior, serve como gatilho para o analista reajustar os pesos estatísticos da fórmula de score.

 - Índice de Satisfação Semântica (NLP) por Segmento: Agrupa a média de sentimentos extraída pelo processador de linguagem natural por nicho de mercado, mapeando setores comerciais com fortes dores operacionais.

## 🧰 Tecnologias Utilizadas

 - Python 3.11 - Núcleo do ecossistema e pipelines.

 - Streamlit - Framework reativo de interface de usuário.

 - PostgreSQL (Supabase) - Armazenamento de dados geográficos e operacionais.

 - Pandas & NumPy - Manipulação matricial de dados e tratamento de nulos.

 - Plotly - Renderização interativa do gráfico de funil executivo.

 - LeIA (Language-Independent Sentiment Analysis) - Biblioteca NLP calibrada para o português brasileiro.

 - psycopg2-binary & RealDictCursor - Driver de baixo nível para comunicação e retorno de dados estruturados em dicionários nativos.

 
## Autor

**Kauã Dias**  

Estudante de Estatística | Data Science | Automação com Python


- GitHub: [Kauadp](https://github.com/Kauadp)

- LinkedIn: [kauad](https://www.linkedin.com/in/kauad/) 