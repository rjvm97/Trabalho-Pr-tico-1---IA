# Trabalho-Pratico-1---IA
Este conjunto de códigos tem por objetivo o aprendizado de forma automática dos carros a andar nas pistas fornecidas.

Os arquivos escretos.py e car.py são os principais para o funcionamento do trabalho, junto ao arquivo individuos.pickle.

Para que se tenha uma correta desenvoltura do código é necessário atentar para os seguintes pontos característicos:

--O numero de carros a ser criado é dado pela variável "n" na main do código car.py, e tal variável é limitada ao número de carros devidamente instanciados em suas coordenadas, com sua respectiva imagem e comandos declarados. Ou seja, se para cada uma dessas características não houver suficientes elementos para os "n" declarados, o algoritmo não executa corretamente.
  Para cada "n" com valor menor do que os suficientes recursos, então o algoritmo executa perfeitamente.

--Antes de executar car.py deve-se observar em qual pista está sendo avaliado o aprendizado dos carros, já que existem dois arquivos para a seleção dos melhores indivíduos de cada pista:
  Para a pista terrain.png, os melhores indivíduos estão salvos no arquivo MelhoresIndividuos2.pickle.
  Para a pista terrain2.png, os melhores indivíduos estão salvos no arquivo MelhoresIndividuos.pickle.
  
--Após essa observação e feitas as alterações necessárias, sempre que o algoritmo for executado as novas gerações são guardadas no arquivo individuos.pickle e, portanto, sempre que for necessário avaliar o aprendizado a partir do instante inicial de todas as gerações já observadas, é necessário executar o arquivo escretos.py para que os indivíduos em individuos.pickle sejam incialmente randômicos.
  Atento ao fato de que, os melhores indivíduos de cada geração sempre são armazenados no mesmo arquivo, cada pista com seu respectivo arquivo, então, para não perder essa informação, é sugerida a criação de novos arquivos "MelhoresIndividuos".pickle para guardar os melhores de cada diferente teste desejado, caso necessário.

O link para melhores explicações do funcionamento e descrição do algoritmo é o seguinte:
