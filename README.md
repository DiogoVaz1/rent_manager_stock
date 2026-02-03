# 📦 Rent Manager Stock

Sistema de gestão de inventário e alugueres desenvolvido à medida para gestão interna de equipamentos. Focado na rapidez de saída de material e controlo de stock em tempo real.

## 🚀 Funcionalidades Principais

* **Gestão de Inventário:** Controlo de produtos, categorias, marcas e números de série.
* **Alugueres:** Registo de saídas e entradas com cálculo automático de dias.
* **Bundles (Kits):** Capacidade de adicionar conjuntos de produtos (ex: "Kit Sala") de uma só vez.
* **Modo Interno:** Gestão de empréstimos para a própria empresa (sem faturação).
* **PDF Automático:** Geração de contratos e folhas de obra em PDF.
* **Painel Administrativo:** Interface limpa e otimizada (Jazzmin), responsiva para telemóvel.

## 🛠️ Tecnologias Usadas

* **Python 3.12**
* **Django 5.x**
* **SQLite** (Base de dados)
* **Django Jazzmin** (Tema de Admin)
* **WeasyPrint** (Geração de PDFs)
* **Bootstrap** (Frontend)

## 💻 Como correr o projeto localmente (No PC)

Se precisares de instalar este projeto num computador novo, segue estes passos:

1.  **Clonar o repositório:**
    ```bash
    git clone [https://github.com/TEU_UTILIZADOR/rent_manager_stock.git](https://github.com/TEU_UTILIZADOR/rent_manager_stock.git)
    cd rent_manager_stock
    ```

2.  **Criar um ambiente virtual:**
    ```bash
    python -m venv venv
    ```

3.  **Ativar o ambiente virtual:**
    * **Windows:** `venv\Scripts\activate`
    * **Mac/Linux:** `source venv/bin/activate`

4.  **Instalar as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Preparar a Base de Dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Criar um Super Utilizador (Admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Ligar o Servidor:**
    ```bash
    python manage.py runserver
    ```
    O site ficará disponível em: `http://127.0.0.1:8000`

## 🌍 Deploy (Servidor)

O projeto está alojado no **PythonAnywhere**.

**Para atualizar o servidor após alterações no GitHub:**
1.  Aceder à consola do PythonAnywhere.
2.  Correr os comandos:
    ```bash
    workon meusite
    cd rent_manager_stock
    git pull
    python manage.py collectstatic  # (Se houver alterações visuais)
    python manage.py migrate        # (Se houver alterações na BD)
    ```
3.  Fazer **Reload** no separador Web.

## 🔒 Licença

Proprietário: **[Nome da Tua Empresa / Teu Nome]**
*Todos os direitos reservados. Uso não autorizado é proibido.*
