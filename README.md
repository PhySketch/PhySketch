# PhySketch
Repositório de base de dados e projeto PhySketch - derivado do trabalho de conclusão de curso "Análise Automática de Rascunhos Offline de Cenários para Simulação de Corpos Rígidos" apresentado no Centro Universitário da FEI em 2018.

## Membros ##
* **Adriana Andrijauskas**
* **Eric Baere Grassl**
* **Fernando de Moraes**
* **Rafael Zulli de Gioia Paiva**



## Como usar
Parametros devem ser definidos para executar os scripts, baseado na IDE PyCharm da Jetbrains, devem ser definidos:
Em Edit Configurations:
* Script path: adicionar o diretório do main.py
* Parameters:
* [ -a ]: necessário quando for utilizado o processo de anotação.
* [ -c ]: necessário quando a opcão de cropped for utilizada.
* [ -i ]: diretório dos arquivos de entrada.
* [ -s ]: inteiro representado o nome da imagem.



### [ -c ] (cropper.py)
**Comandos primários:**
* N: passa a imagem.
* 1: comando referente a atividade 1.
* 2: comando referente a atividade 2.
* 3: comando referente a atividade 3.
**Comandos secundários:**
* R: reseta o comando informado.
* C: corta.
**Comandos terciários:**
* C: cancela.
* S: salva.

**Fluxo principal**
* Encontra a imagem que deseja cortar (N).
* Seleciona a atividade (1, 2 ou 3). **[FS1]**
* Corta os elementos (C).
* Salva os cortes (S). **[FS2]**
* Fim.
**[FS1]**
Nome: deseja mudar o número de atividade.
* Reseta o comando informado (R).
* Volta para o fluxo principal.
**[FS2]**
Nome: não quer salvar os cortes.
* Cancela (C).
* Fim.



### [ -c ] (annotator.py)
**Comandos primários:**
* N: passa a imagem.
* 1: comando referente a elemento individual.
* 2: comando referente a cenário.
**Comandos secundários de elemtos individuais:**
* 1: círculo?
* 2: quadrado?
* 3: triângulo equilátero?
* 4: triângulo retângulo?
* 5: triângulo obtusângulo?
* 6: ponto fixo?
* 7: seta? (apenas centro do comando)
* 8: corda?
* 9: ponto de rotação?
**Comandos secundários de cenários:**
* Q: sai.
**Comandos gerais secundários/terciários:**
* R: recomaça a anotação.
* C: limpa as marcações referente àquele elemento.
* S: salva.

**Fluxo principal referente à um elemento individual**
* Encontra a imagem que deseja anotar (N).
* Seleciona elemento (1).
* Seleciona o número do elemento (1, 2, 3, 4, 5, 6, 7, 8 ou 9). **[FS1]**
* Anota o elemento, onde sigam as seguintes especificidades:
* *1: seleciona o centro e mais três pontos.
* *2:
* *3:
* *4:
* *5:
* *6:
* *7:
* *8:
* *9:
* Salva a anotação (S). **[FS2]**
* Fim.
**[FS1]**
Nome: deseja mudar o número de elemento.
* Recomeça a anotação (R).
* Volta para o fluxo principal.
**[FS2]**
Nome: deseja mudar a anotação.
* Limpa a anotação já realizada (C).
* Volta para o fluxo principal.

**Fluxo principal referente à um cenário**
* Encontra a imagem que deseja anotar (N).
* Seleciona cenário (2).
* Seleciona o elemento que você deseja anotar, iniciando sempre pelos corpos (1, 2, 3, 4, 5, 6, 7, 8 ou 9). **[FS1]**
* Anota o corpo, seguindo o "Fluxo principal referente à um elemento individual". **[FS2]**
* Salva a anotação (S). **[FS3]**
* Fim.
**[FS1]**
Nome: deseja mudar o número de elemento.
* Recomeça a anotação (R).
* Volta para o fluxo principal.
**[FS2]**
Nome: elemento individual é comando
* Selecione o centro do elemento.
* Digite o número referente ao corpo parente do elemento (número sequencial, seguindo a ordem de anotação).
* Volta para o fluxo principal.
**[FS3]**
Nome: deseja mudar a anotação.
* Limpa a anotação já realizada (C).
* Volta para o fluxo principal.
