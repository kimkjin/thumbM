# thumbM

Software simples feito em python, com o objetivo de salvar screenshots de forma randomica de todos os videos .MP4, .MKV, .AVI ou webM que tem em uma pasta. Foi programado por padrão para igonrar os primeiros 5min e os ultimo 3min de cada video.

<p align="center">
  <img src="https://raw.githubusercontent.com/kimkjin/mimgs/main/imagem_2023-07-10_033335049.png" width="640" alt="thumbM pic">
</p>



## **[Download v1.0.0](https://github.com/kimkjin/thumbM/releases/tag/v1.0)** 

## Recursos
- Screenshot randomica de frames de um vídeos
- Screenshot salvas no formato .WebP
- Exclusão dos primeiros 5 minutos e últimos 3 minutos de cada vídeo (pode ser alterado)
  
  ```python
  frames_to_skip_start = int(frame_rate * 60 * 5)  # 5 minutos
  frames_to_skip_end = int(frame_rate * 60 * 3)  # 3 minutos
  ```
  
- Verificação da presença de legendas nos frames. Verificar as cores da legenda caso ela continue aparecendo nas screenshots.

  ```python
  LEGEND_COLOR_CODES = ['#ffffff', '#000002', '#000000']
  ```

### Frames a serem analisados
- O software faz uma analise de 6.000 frames randomicos, até encontrar um que se encaixe nas regras que foram propostas. Quanto maior for o numero, maior vai ser o tempo de processamento, porém se o numero for muito baixo também existe a chance da screenshot não ser salva, já que o codigo trabalha por processo de eliminação. Ex:
  
  ```python
  # Aqui 10 frames estão sendo setados, se houver legendas nos 10 frames o processamento vai terminar e uma mensagem de aviso será gerada.
  NUM_RANDOM_FRAMES = 10
  ```
  
- Seleção de frames com no mínimo 256 cores de paletas diferentes (teste)

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
