# Renderizador
Renderizador base para o curso de Computação Gráfica

Pré-requisitos:

```sh
pip3 install -r requirements.txt
````

Uso:
```sh
  python3 renderizador.py
````

Opções
- "-i", "--input": arquivo X3D de entrada
- "-o", "--output": arquivo 2D de saída (imagem)
- "-w", "--width": resolução horizontal
- "-h", "--height": resolução vertical
- "-q", "--quiet": não exibe janela

## Exemplos

Para rodar os exemplos:

```sh
  python3 exemplos.py
````

Opções:
- número ou índice do exemplo

Visualizar exemplos na web:

[Exemplos](https://lpsoares.github.io/Renderizador/)

Lista de exemplos:

0. pontos
1. linhas
2. octogono
3. tri_2D
4. helice
...

Se quiser ver os arquivos localmente, rode: python3 -m http.server

## Funcionalidades Adicionadas

As seguintes funcionalidades foram implementadas/atualizadas neste fork:

1. Z-buffer (Depth Test)
  - Framebuffer agora aloca um attachment de profundidade (DEPTH_COMPONENT32F).
  - O valor de profundidade é inicializado com 1.0 (mais distante); valores menores (mais próximos) substituem o pixel.
  - Conversão usada: z_ndc em [-1,1] -> depth = (z_ndc + 1)/2.

2. Interpolação com correção de perspectiva
  - `GL.triangleSet` e `GL.indexedFaceSet` agora carregam 1/w e aplicam interpolação perspective-correct para Z e (quando disponíveis) cores ou coordenadas de textura.
  - Para textura e cor por vértice: valores são combinados usando pesos baricêntricos ajustados por 1/w.

3. Transparência simples
  - Campo `transparency` do material (0=opaco, 1=totalmente transparente) aplicado após aprovação no depth test.
  - Blending: `final = src*(1-alpha) + dst*alpha`.
  - Ordem de desenho ainda importa (não há ordenação nem composição avançada); ideal para objetos levemente transparentes ou cena simples.

4. Super-Sampling Anti-Aliasing (SSAA)
  - Agora ativado por padrão em 2x2 (`ssaa_factor = 2`).
  - Pode ser desativado definindo `ssaa_factor = 1` antes do `setup()`.
  - Downsample usa média simples (box filter). Pode-se evoluir para filtro gaussiano.

5. Texturas com Mipmaps
  - Ao carregar uma textura (`ImageTexture`) é construída pirâmide de níveis até 1x1.
  - Seleção de nível heurística por variação de UV e área de triângulo em tela.
  - Minimiza aliasing em objetos distantes e reduz shimmering.

## Próximos Passos Sugeridos
 - Mipmapping para texturas (atual é single sample).
 - Suporte a canal alfa completo (usar RGBA8) para melhor blending acumulativo.
 - Ordenação de faces transparentes ou técnica de weighted blended OIT.
 - Iluminação (normais e modelo de Phong/Gouraud) e normal mapping.
 - Otimizações: early-z, hierarquia de bounding boxes, SIMD em loops de raster.

## Notas Internas
 - A conversão para coordenadas de tela segue origem no canto superior esquerdo.
 - Regra Top-Left usada para preenchimento garante ausência de gaps entre triângulos adjacentes.
 - Qualquer ajuste em projeção deve manter coerência com formulação do depth test descrita acima.

