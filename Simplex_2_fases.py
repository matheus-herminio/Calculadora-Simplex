from sys import stdin
import itertools
EPS = 1e-4


# Feito por: Matheus Herminio Da Silva RA: 201027747
#

# Exemplo de entrada para o código:
# 2x1 + x2 <= 8
# x1 + 2x2 <= 7
# x2 <= 3
# Max: x1 + x2
# n, m = 3, 2
# a = [[2,1],[1,2],[0,1]]
# b = [8, 7, 3]
# c = [1, 1]
class Position:
    def __init__(self, coluna, linha):
        self.coluna = coluna
        self.linha = linha

def LerEq():
    print("Quantas restrições e quantas variaveis tem o problema?")
    print("Exemplo de entrada: '3 2' para 3 restrições e 2 variaveis")
# Recebe um número inteiro "m" que define quantas variáveis existem no total
# Recebe um número inteiro "n" que define quantas equações de restrições há no total
    z = input()
    n, m = map(int, z.split())
    a = []
    print("Escreva as restrições sem seus custos, você pode colocar tudo junto, antes de dar o enter:")
    print("Exemplo de entrada: ")
    print("2 1")
    print("1 2")
    print("0 1")
    print("Para: 2x1 + x2")
    print("      1x1 + 2x2")
    print("            2x2")
# Recebe uma lista de listas "a" de tamanho n x m que contém as restrições.
    for linha in range(n):
        a.append(list(map(float, input().split())))
    print("Insira os valores de b:")
    print("Exemplo de entrada: '8 7 3' para 2x1 + x2 <= 8")
# Recebe uma lista "b" de tamanho n dos máximos de cada desigualdade
    b = list(map(float, input().split()))
    print("Insira a expressão de maximização, caso vc esteja usando minimização, multiplique tudo por -1 e insira abaixo")
    print("Exemplo de entrada: '1 1' para Max z = x1 + x2")
# Recebe uma lista "c" que representa a função de otimização a ser maximizada
    c = list(map(float, input().split()))
    return a, b, c, n, m

# Um tableau é criado com tamanho (m + n + 1) x (n + 1). Cada restrição é colocada em uma linha no tableau e uma variável de folga é adicionada a
# cada restrição. Uma variável de folga em equações de desigualdade é adicionada para transformar as equações em igualdades.
# No exemplo fornecido, o tableau teria a seguinte aparência para o formato padrão:
# [ 1,  1, -3, 1, 0, 0, 10]
# [-5, 10,  0, 0, 1, 0, 50]
# [ 3, -2, -4, 0, 0, 1,  9]
# [-1, -6,  3, 0, 0, 0,  0]
def CriaTableaux(a, b, c, n, fase_um_otimizacao):
  tableau = []
  fase_um_linha = [0] * (len(c) + n + 2)
  for i in range (n):
      # Para a otimização da fase 1 no método simplex de 2 fases, qualquer desigualdade que tenha uma solução inferior a zero será invertida
      # Por exemplo, 2x -3y <= -10 --> -2x + 3y <= 10
      # A variável de folga é adicionada ao tableau com o valor -1 para levar em conta a inversão do sinal
    if fase_um_otimizacao and b[i] < 0:
      slack_variaveis = [0] * n
      slack_variaveis[i] = -1.0
      tableau_linha = [-1*x for x in a[i]] + slack_variaveis + [-1 * b[i]]
      tableau.append(tableau_linha)
      fase_um_linha = [a + b for a, b in zip(fase_um_linha, tableau_linha)]
    else:
      slack_variaveis = [0] * n
      slack_variaveis[i] = 1.0
      tableau_linha = a[i] + slack_variaveis + [b[i]]
      tableau.append(tableau_linha)
  final_linha = [-1*x for x in c] + [0] * n + [0]
  tableau.append(final_linha)
  return tableau, fase_um_linha

# A Regra de Bland será usada para a seleção do elemento pivô:
# 1. Escolha a coluna mais à esquerda que é negativa
# 2. Entre as linhas, escolha aquela com a menor razão entre o lado direito do tableau (valor b) e o coeficiente da coluna onde o coeficiente é maior que zero.
# 2 (continuação). Se a razão mínima for compartilhada por várias linhas, escolha a linha com a variável de coluna mais baixa (variável básica) nela.
# Para o #2, o algoritmo não apenas pega a mínima razão baixa porque o caso especial de múltiplos mínimos deve ser considerado. Além disso, a regra de Bland pede a variável básica mais baixa -
# numerada, que é diferente do índice mais baixo. Para isso, o algoritmo mantém um registro da variável básica na lista "slack_linhas"
def SelecionaElemento(a, m, slack_linhas, fase_um_otimizacao, fase_um_linha):
    pivo_element = Position(0, 0)
    no_solucao = False
    if fase_um_otimizacao:
      pivo_element.coluna = fase_um_linha.index(max(fase_um_linha[:-1]))
    else:
      pivo_element.coluna = a[len(a)-1][:-1].index(min(a[len(a)-1][:-1])) # Escolhe o mínimo no index
    ratios = []
    if pivo_element.coluna != None:
      for r in range(len(a)-1):
        if a[r][pivo_element.coluna] > 0:
            ratios.append(abs(a[r][-1] / a[r][pivo_element.coluna]))
        else:
          ratios.append(float("inf"))
      if all(i == float("inf") for i in ratios):
        no_solucao = True
      linha_min = min(ratios)
      linha_min_indicies = [i for i,x in enumerate(ratios) if x == linha_min]
      # Escolhe o menor em caso de empate na escolha
      if (len(linha_min_indicies) > 1):
        least_variable = []
        for j in linha_min_indicies:
          least_variable.append(slack_linhas[j])
        pivo_element.linha = slack_linhas.index(min(least_variable))
      else:
        pivo_element.linha = linha_min_indicies[0]
    else:
      no_solucao = True
    return no_solucao, pivo_element

#Processa o pivô escolhido, sempre será o valor de zero, então já é colocado na solução
def ProcessaElemento(a,pivo_element, fase_um_otimizacao, fase_um_linha):
    pri_mult = a[pivo_element.linha][pivo_element.coluna] #Multiplicador primário
    a[pivo_element.linha] = [n / pri_mult for n in a[pivo_element.linha]] #Faz o elemento ter valor 1
    a[pivo_element.linha][pivo_element.coluna] = 1.0
    for i in range(len(a)):
      if i != pivo_element.linha:
        sec_mult = a[i][pivo_element.coluna] #Atualizando o multiplicador secundário
        pri_linha = [j * sec_mult for j in a[pivo_element.linha]]
        a[i]= [a- b for a, b in zip(a[i], pri_linha)]
        a[i][pivo_element.coluna] = 0
    if fase_um_otimizacao:
      sec_mult = fase_um_linha[pivo_element.coluna] #Atualizando o multiplicador secundário
      pri_linha = [j * sec_mult for j in a[pivo_element.linha]]
      fase_um_linha = [a- b for a, b in zip(fase_um_linha, pri_linha)]
      fase_um_linha[pivo_element.coluna] = 0
    return a, fase_um_linha

#Este algoritmo vai tentar resolver pelo método mais simples, mas caso o seja necessário a segunda fase, ele o manda para a função
def Resolve(a, b, c, n, m):
    if all(i <= 0 for i in c) and all(i >= 0 for i in b):
      return [0] * m
    tableau, fase_um_linha = CriaTableaux(a, b, c, n, False)
    ans, fase_um_answer = resolveTableaux(tableau, a, b, m, n, False, fase_um_linha)
    #Para caso o tableaux seja infinito
    if ans == [-1] or ans == [float("inf")]:
      return ans
    invalid_answer = validaresposta(ans, a, b, m, n)
    #Procede para a segunda fase do simplex
    if invalid_answer:
      tableau, fase_um_linha = CriaTableaux(a, b, c, n, True)
      ans, fase_um_answer = resolveTableaux(tableau, a, b, m, n, True, fase_um_linha)
      fase_um_answer_invalid = validaresposta(fase_um_answer, a, b, m, n)
      if ans == [-1] or ans == [float("inf")]:
        return ans
      invalid_answer = validaresposta(ans, a, b, m, n)
    if invalid_answer:
      if not fase_um_answer_invalid:
        return fase_um_answer
      else:
        return [-1]
    return ans

# Verifica a validade da resposta
def validaresposta(ans, a, b, m, n):
  invalid_answer = False
  for i in range(n):
        valid_ans = 0
        for j in range(m):
          valid_ans += a[i][j] * ans[j]
        if epsilon_greater_than(valid_ans, b[i]):
          invalid_answer = True
  if not all(epsilon_greater_than_equal_to(i, 0) for i in ans):
    invalid_answer = True
  return invalid_answer

# Resolce o tableaux
def resolveTableaux(tableau, a, b, m, n, fase_um_otimizacao, fase_um_linha):
  slack_linhas = list(range(m,n+m))
  fase_um_complete = False
  fase_um_answer = [0] * m
  while (fase_um_otimizacao or not all(epsilon_greater_than_equal_to(i, 0) for i in tableau[len(tableau)-1][:-1])):
    if fase_um_otimizacao and all(epsilon_less_than_equal_to(k, 0) for k in fase_um_linha[:-1]):
      fase_um_otimizacao = False
      fase_um_complete = True
      fase_um_answer = manda_resposta(tableau, slack_linhas)
      if all(epsilon_greater_than_equal_to(i, 0) for i in tableau[len(tableau)-1][:-1]):
        break
    no_solucao, pivo_element = SelecionaElemento(tableau, m, slack_linhas, fase_um_otimizacao, fase_um_linha)
    if no_solucao:
      if fase_um_complete:
        return [-1], fase_um_answer
      else:
         return [float("inf")], fase_um_answer
    slack_linhas[pivo_element.linha] = pivo_element.coluna
    tableau, fase_um_linha = ProcessaElemento(tableau, pivo_element, fase_um_otimizacao, fase_um_linha)
  return manda_resposta(tableau, slack_linhas), fase_um_answer

#Acha a resposta
def manda_resposta(tableau, slack):
  ans = [0] * m
  for i in range(n+m):
    if i < m and i in slack:
      index = slack.index(i)
      ans[i] = tableau[index][-1]
    elif i not in slack and tableau[-1][i] == 0:
      for j in range(n-1):
        if tableau[j][i] > 0:
          return [-1]
    elif i < m:
      ans[i] = 0
  return ans

#Mede a igualdade ou desigualdade de 2 números em relação a epslon
def epsilon_greater_than(a, b):
  return ((a > b) and not isclose(a, b))

def epsilon_greater_than_equal_to(a, b):
  return ((a > b) or isclose(a, b))

def epsilon_less_than(a, b):
  return ((a < b) and not isclose(a, b))

def epsilon_less_than_equal_to(a, b):
  return ((a < b) or isclose(a, b))

def isclose(a, b):
    return abs(a-b) <=EPS

# Faz o print da Coluna resposta
def Printcoluna(coluna):
    size = len(coluna)
    if size == 1 and coluna[0] == -1:
      print("Sem Solução")
    elif size == 1 and coluna[0] == float("inf"):
      print("Solução infinita")
    else:
      print("Solução limitada")
      print(' '.join(list(map(lambda x : '%.2f' % x, coluna))))

if __name__ == "__main__":
    print("Calculadora de Simplex 2 fases, este programa usa como forma padrão a máximização, insira o que for pedido")
    a, b, c, n, m = LerEq()
    sol = Resolve(a, b, c, n, m)
    Printcoluna(sol)
    exit(0)