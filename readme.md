# Contexto
Se baseia no modelo de negócio que funciona com base na troca de livros pelos usuários, cada livro cadastrado pelo usuário dá o direito a uma troca, porém o usuário também pode comprar o livro caso não queira oferecer outro em troca.

Uma das ferramentas importantes para que esse modelo de negócio rentabilize, é a recomendação. Uma excelente recomendação aumenta o volume de trocas e vendas no site.

A partir desse ponto a startup objetiva construir um sistema de recomendação com atualizações diárias a partir dos dados do site. Entretanto a mesma não coleta e nem armazena os livros enviados pelos usuários.
 
Os livros para troca, são enviados pelos próprios usuários através de um botão “Fazer Upload”, eles ficam visíveis no site, junto com suas estrelas, que representam o quanto os usuários gostaram ou não do livro. 

# Objetivo

Criar um scrap para armazenamento no banco de dados a partir da imagem do site no momento da coleta.
    
Dados coletados:
- Nome do Livro
- Categoria
- O numero de estrelas recebidas
- Preço do livro
- Se o livro se encontra em estoque ou não.

# Método e libs empregadas

* Método:

    O Método adotado, devido necessitar coletar informação de categorias, foi de percorrer as mesmas, realizando uma coleta cíclica e tratando os dados em cada página, na posteriori realizando a inserção de imediato no banco de dados criando a imagem necessária.

    Deste modo, sempre que o script entrar em execução, ele excluirá a tabela existente criando outra e alimentando com os dados da imagem mais recente do site.

* Libs empregadas:

    - Pandas: Torna a manipulação dos dados mais rápida e fácil a partir do modelo de   
              Dataframe e ainda permite através do 'pandas.io' executar comandos sql diversos.   
    - selenium: Fornece as ferramentas necessárias para coleta.
    - word2number: Durante o tratamento converte números por extenso em inteiros.
    - sqlalchemy: Cria a engine necessária para manipular do Banco de dados.



# Funções

* drive_init(): Inicia e retorna o webdriver utilizado.

* engine_init(): Inicia e retorna a engine utilizada para o banco de dados, como também define esquema de tabela para o banco de dados caso não exista, e exclui a tabela antiga caso exista.

* scrapy_category_lists(driver): 
    * Realiza um get na página incial do site, percorrendo toda lateral coletando os links que direcionam para as categorias, realiza ainda o tratamento desses links extraindo os nomes das categorias. 
    * Objetiva fornecer 2 listas a primeira com a lista de links e a segunda com a lista de categorias correspondentes.

* scrapy_rows(driver): 
    * Procura encontrar a partir do path e listar todas as linhas de informação concernentes ao livros em exibição no link vigente. 
    * Objetiva retornar uma lista com todas as linhas de informação 

* extract_data(rows:list, category: str):
    * Processa e limpa as informações coletando, títulos, preços, booleano de status de estoque, informação de rating em inteiros, e adicionando a categoria.
    * Objetiva extrair e tratar os dados afim de fornecer uma estrutura de dicionário apropriada para conversão em Dataframe. 

* to_postgres(data,engine,schema='book_club', table='books'): 
    * Realiza a conversão dos dados para dataframe, em seguida cria a tabela necessária e define seus respectivos tipos de dados automaticamente, por fim realiza a inserção dos dados no Postgres.
    * Objetiva inserir os dados extraídos no banco de dados. 

* extract_next_page(driver):
    * Realiza a checagem se há uma próxima página para extração.
    * Objetiva retornar a url da próxima página caso exista, motivando assim a execução de um novo ciclo. 
    
* sql_image_to_csv(engine): 
    * Função extra o qual objetiva realizar uma consulta no banco de dados após a gravação final e gerar uma saida csv. 

* extration_clycle(url, category,engine): 
    * Direciona a página qual deve ser direcionada a extração. Destarte por sequência realiza a chamada de extração de dados e armazenamento no postgres, e por fim, faz a chamada da função que extrai o link da próxima página se houver. 
    * Objetiva consolidar um ciclo de atualização, extração , armazenamento, e indicar a url necessária para o próximo ciclo.

* def process(driver, engine):
    *Objetiva coordenar toda execução do programa. 


# Utilização

A para utilizar certifique-se de possuir as libs necessárias, disponíveis em requirements.txt, e o chromedriver correto para seu navegador, como também inserir:
(<o path referente a sua localização>,<options=option>) no webdriver.  

Por fim basta indicar o banco de dados. E executar o script. 


Obs: Os testes foram criados utilizando o pytest. E foi definido action para testagem a cada push. 
