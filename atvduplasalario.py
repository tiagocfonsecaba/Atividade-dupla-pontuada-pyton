import os

# Lista para armazenar os usuários cadastrados
usuarios_cadastrados = []

def limpar_tela():
    os.system("cls")

def cadastrar_usuario():
    print("=== CADASTRO DE USUÁRIO ===")
    usuario = input("Insira o número da sua matrícula: ").strip()
    senha = input("Crie uma senha: ").strip()
    
    usuarios_cadastrados.append({"usuario": usuario, "senha": senha})
    print("\nUsuário cadastrado com sucesso!")
    input("Pressione ENTER para ir para o login...")

def autenticar_usuario():
    limpar_tela()
    print("=== LOGIN NO SISTEMA ===")
    tentativas = 3
    
    for i in range(tentativas):
        usuario_digitado = input("Matrícula: ").strip()
        senha_digitada = input("Senha: ").strip()
        
        # Verifica se a matrícula e a senha batem dentro do loop
        for conta in usuarios_cadastrados:
            if conta["usuario"] == usuario_digitado and conta["senha"] == senha_digitada:
                print("\nAutenticação realizada com sucesso!")
                input("Pressione ENTER para acessar a folha de pagamento...")
                return usuario_digitado
        
        # Se errar, avisa quantas tentativas restam
        restantes = tentativas - (i + 1)
        if restantes > 0:
            print(f"\nErro: Matrícula ou senha incorretos. Restam {restantes} tentativa(s).\n")
        else:
            print("\nLimite de tentativas encerrado. Acesso bloqueado!")
            
    return None

def calcular_inss_2026(salario_base):
    # Tabela progressiva oficial do INSS 2026 (com parcela a deduzir)
    if salario_base <= 1621.00:
        return salario_base * 0.075
    elif salario_base <= 2902.84:
        return (salario_base * 0.09) - 24.32
    elif salario_base <= 4354.27:
        return (salario_base * 0.12) - 111.40
    elif salario_base <= 8475.55:
        return (salario_base * 0.14) - 198.49
    else:
        # Teto máximo do INSS em 2026
        return (8475.55 * 0.14) - 198.49  # R$ 988,09

def calcular_irrf_2026(salario_base, desconto_inss, dependentes):
    # Regra 2026: Isenção total para rendimentos até R$ 5.000,00
    if salario_base <= 5000.00:
        return 0.0, 0.0

    # Dedução por dependente em 2026: R$ 189,59
    deducao_dependentes = dependentes * 189.59
    
    # A legislação permite usar as deduções legais (INSS + dependentes) ou o desconto simplificado (R$ 607,20)
    deducao_total = max(desconto_inss + deducao_dependentes, 607.20)
    base_calculo = salario_base - deducao_total

    if base_calculo <= 2428.80:
        ir_bruto = 0.0
    elif base_calculo <= 2826.65:
        ir_bruto = (base_calculo * 0.075) - 182.16
    elif base_calculo <= 3751.05:
        ir_bruto = (base_calculo * 0.15) - 394.16
    elif base_calculo <= 4664.68:
        ir_bruto = (base_calculo * 0.225) - 675.49
    else:
        ir_bruto = (base_calculo * 0.275) - 908.73

    # Redutor adicional de 2026 para quem ganha entre R$ 5.000,01 e R$ 7.350,00
    if salario_base <= 7350.00:
        redutor = 978.62 - (0.133145 * salario_base)
        ir_final = ir_bruto - max(0.0, redutor)
    else:
        ir_final = ir_bruto

    ir_final = max(0.0, ir_final)
    percentual_irrf = (ir_final / salario_base) * 100
    
    return ir_final, percentual_irrf

def gerar_contracheque(nome_usuario):
    limpar_tela()
    print("=== DADOS PARA CÁLCULO DA FOLHA ===")
    
    salario_base = float(input("Digite o salário base (R$): "))
    if salario_base < 0:
        print("Valor inválido.")
        return

    dependentes = int(input("Digite a quantidade de dependentes: "))
    if dependentes < 0:
        print("Quantidade de dependentes inválida.")
        return

    # 1. Vale-Transporte (Desconto legal de até 6% do salário base, limitado ao valor gasto)
    quer_vt = input("Deseja solicitar Vale-Transporte? (s/n): ").strip().upper()
    if quer_vt in ["S", "SIM"]:
        valor_passagens = float(input("Digite o valor mensal gasto com passagens (R$): "))
        desconto_vt = min(salario_base * 0.06, valor_passagens)
    else:
        desconto_vt = 0.0

    # 2. Vale-Refeição (Desconto padrão de 20% sobre o valor do benefício concedido)
    valor_vr = float(input("Digite o valor total do Vale-Refeição recebido (R$): "))
    desconto_vr = valor_vr * 0.20

    # 3. Plano de Saúde (Valor fixo mensal + adicional por dependente, exemplo: R$ 150,00 por pessoa)
    tem_plano = input("Possui Plano de Saúde da empresa? (s/n): ").strip().upper()
    if tem_plano in ["S", "SIM"]:
        desconto_saude = 150.00 * (1 + dependentes)
    else:
        desconto_saude = 0.0

    # Cálculos dos impostos oficiais
    desconto_inss = calcular_inss_2026(salario_base)
    desconto_irrf, percentual_irrf = calcular_irrf_2026(salario_base, desconto_inss, dependentes)

    # Totais
    total_descontos = desconto_inss + desconto_irrf + desconto_vt + desconto_vr + desconto_saude
    salario_liquido = salario_base - total_descontos

    # Monta a descrição com o percentual
    descricao_irrf = f"IRRF ({percentual_irrf:.1f}%)"

    # Exibição do Contracheque formatado
    limpar_tela()
    print("=" * 52)
    print(f"{'CONTRACHEQUE / DEMONSTRATIVO DE PAGAMENTO':^52}")
    print("=" * 52)
    print(f"Matrícula: {nome_usuario:<24} Dependentes: {dependentes}")
    print("-" * 52)
    print(f"{'DESCRIÇÃO':<30} | {'PROVENTOS':>8} | {'DESCONTOS':>8}")
    print("-" * 52)
    print(f"{'Salário Base':<30} | {salario_base:>8.2f} | {'':>8}")
    print(f"{'INSS (Previdência)':<30} | {'':>8} | {desconto_inss:>8.2f}")
    print(f"{descricao_irrf:<30} | {'':>8} | {desconto_irrf:>8.2f}")
    print(f"{'Vale-Transporte (6%)':<30} | {'':>8} | {desconto_vt:>8.2f}")
    print(f"{'Vale-Refeição (20% PAT)':<30} | {'':>8} | {desconto_vr:>8.2f}")
    print(f"{'Plano de Saúde':<30} | {'':>8} | {desconto_saude:>8.2f}")
    print("-" * 52)
    print(f"{'TOTAIS':<30} | {salario_base:>8.2f} | {total_descontos:>8.2f}")
    print("=" * 52)
    print(f"{'SALÁRIO LÍQUIDO A RECEBER:':<35} R$ {salario_liquido:>11.2f}")
    print("=" * 52)

# --- FLUXO PRINCIPAL ---
limpar_tela()
cadastrar_usuario()
usuario_logado = autenticar_usuario()

if usuario_logado:
    gerar_contracheque(usuario_logado)
