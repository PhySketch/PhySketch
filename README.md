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
**Comandos:**
* N: passa a imagem.
* 1: comando referente a atividade 1.
* 2: comando referente a atividade 2.
* 3: comando referente a atividade 3.
* R: reseta o comando informado.
* C: corta.
* C depois do C: cancela.
* S depois do C: salva.
