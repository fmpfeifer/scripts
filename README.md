# scripts

Scripts para geração de mídia flash com relatórios do cellebrite.
Os scripts são escritos em python, então é necessário ter o interpretador python instalado. Recomenda-se o python 3.8 ou superior, mas o script deve funcionar com python 3.6 em diante (foi testado apenas em 3.8 e 3.9).

## converte_wav.py

Script para converter arquivos convertidos pelo Cellebrite para wav em mp3, de forma a economizar espaço.
Uso:

```
python converte_wav.py Pasta_Relatorio
```

Exemplo:

```
python converte_wav.py D:\Report\CasoA_Midia
```

O script vai varrer toda a estrutura de diretórios procurando por arquivos com nome terminados em “\_Converted.wav”. Para cada arquivo alvo encontrado, usa o programa ffprobe.exe para verificar se realmente se trata de um arquivo wav. Caso afirmativo, o arquivo é renomeado (acrescentando-se a extensão “\_oldwav”), e então convertido para mp3. O nome do arquivo convertido é o mesmo do arquivo original (inclusive a extensão wav). O arquivo original (renomeado) é então apagado.
Caso o script seja executado uma segunda vez na mesma pasta, nenhum arquivo será convertido, pois o ffprobe.exe o identificará como mp3, e não wav.

## deduper.py

Script para cópia de arquivos para a mídia flash. Uso:

```
python deduper.py Pasta_origem Pasta_destino
```

Exemplo:

```
python deduper.py D:\Report\CasoA_Midia H:
```

O script checa o hash de cada arquivo. Se o arquivo já existir no destino, só sobrescreve se o hash for diferente (não copia novamente arquivos já no destino). Pode-se executar várias vezes para corrigir arquivos corrompidos na mídia de destino (recomenda-se ejetar o pendrive e executar novamente o script para verificar e corrigir arquivos porventura corrompidos).
O script não apaga arquivos presentes no destino que não estão presentes na origem.
A pasta de destino deve estar em um sistema de arquivos NTFS. Quando o script encontra um segundo arquivo idêntico a um arquivo já copiado (mesmo tamanho e hash), ao invés de copiar o arquivo, é criado no destino um _hardlink_ para o arquivo já copiado, para economizar espaço na mídia de destino. Por isso a necessidade de estar formatado com NTFS (suporte a _hardlink)_.
