# 🏋️ Dashboard de Avaliação Física

Dashboard interativo em **Streamlit** para gerenciamento de avaliações físicas de múltiplos clientes.

## ✨ Funcionalidades

- **📋 Cadastro de Clientes**: Nome, gênero, data de nascimento, biotipo
- **📊 Composição Corporal**: IMC, TMB, gasto calórico diário
- **📏 Perímetros Corporais**: 19 medidas com gráfico radar
- **📈 Evolução**: Histórico de avaliações com gráficos comparativos
- **📄 Relatórios**: Exportação para Excel

## 🚀 Como Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o dashboard
streamlit run aplicativo.py
```

O aplicativo estará disponível em: **http://localhost:8501**

## 📁 Estrutura do Projeto

```
├── aplicativo.py           # Ponto de entrada principal
├── paginas/                # Páginas do dashboard
│   ├── pagina_dashboard.py
│   ├── pagina_clientes.py
│   ├── pagina_avaliacao.py
│   ├── pagina_historico.py
│   └── pagina_relatorios.py
├── componentes/            # Componentes visuais
│   ├── cartao_perfil.py
│   ├── grafico_radar.py
│   ├── grafico_evolucao.py
│   └── indicadores_kpi.py
├── servicos/               # Lógica de negócio
│   ├── calculadora_corporal.py
│   └── analisador_perimetros.py
├── dados/                  # Persistência
│   ├── gerenciador_clientes.py
│   ├── gerenciador_avaliacoes.py
│   └── clientes.json
└── requirements.txt
```

## 📊 Screenshots

### Dashboard Principal
- KPIs com Peso, IMC, TMB e Gasto Calórico
- Gráfico radar de perímetros corporais
- Gráfico de evolução de peso

### Página de Avaliação
- Formulário completo com todos os perímetros
- Cálculos em tempo real
- Organização por abas (Superiores, Tronco, Inferiores)

## 🛠️ Tecnologias

- **Python 3.10+**
- **Streamlit** - Interface web
- **Pandas** - Manipulação de dados
- **Plotly** - Gráficos interativos
- **OpenPyXL** - Exportação Excel

## 📝 Critérios de Código

Este projeto segue boas práticas de Clean Code:
- ✅ Código em Português-BR
- ✅ Nomenclatura descritiva
- ✅ Funções pequenas e modulares
- ✅ Separação de responsabilidades

## 📄 Licença

MIT License
