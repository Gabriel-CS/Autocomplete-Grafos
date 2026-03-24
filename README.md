# 🌳 AutoComplete com AVL e Teoria dos Grafos

![Status](https://img.shields.io/badge/status-concluído-success)

## 📖 Sobre o Projeto

Este projeto foi desenvolvido como trabalho final da disciplina de **Introdução à Teoria dos Grafos**. O objetivo principal foi aplicar os conhecimentos adquiridos em sala de aula, focando especificamente em **estruturas de árvores com pesos**, mais precisamente **Árvores AVL**.

A aplicação prática escolhida foi a construção de um **Sistema de Autocomplete** inteligente para a língua portuguesa. O sistema utiliza uma estrutura de grafo/árvore para organizar um banco de dados de palavras e sugerir termos similares à medida que o usuário digita, baseando-se em métricas de distância e prefixos.

## 🚀 Funcionalidades

- **Autocomplete em Tempo Real:** Sugestão de palavras enquanto o usuário digita.
- **Estrutura AVL:** Balanceamento automático para garantir eficiência na busca (O(log n)).
- **Pré-processamento com N-grams:** Separação de palavras em subconjuntos de *n-letras* para verificação eficiente de prefixos.
- **Análise Reversa (Palíndromos):** Inversão de palavras para verificar prefixos em direções diferentes, ampliando a capacidade de sugestão.
- **Métrica de Distância:** Algoritmo que prioriza sugestões com a menor distância de edição possível em relação ao input do usuário.

## 🛠️ Metodologia

O funcionamento do sistema baseia-se nos seguintes pilares:

1. **Coleta de Dados:** Utilização de um banco de dados extenso de palavras em português.
2. **Geração de N-grams:** Criação de 3 bancos de dados derivados, fragmentando as palavras para otimizar a busca por similaridade.
3. **Construção do Grafo:** As palavras são inseridas na estrutura AVL, tratando a árvore como um grafo direcionado para navegação.
4. **Busca e Sugestão:** Ao receber um input, o sistema analisa os prefixos (normais e invertidos) e calcula a distância para retornar as palavras mais próximas que atendem aos requisitos mínimos.

## 💻 Tecnologias Utilizadas

*   **Linguagem:** [Python]
*   **Estrutura de Dados:** Árvore AVL (Weighted Tree)
*   **Conceitos:** Teoria dos Grafos, N-grams, Distância de Edição
*   **IDE:** [VS Code]

## 📦 Como Rodar o Projeto

Siga os passos abaixo para executar o sistema localmente:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
