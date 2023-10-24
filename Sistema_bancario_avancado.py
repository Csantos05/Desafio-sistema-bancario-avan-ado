import textwrap
from abc import ABC, abstractclassmethod, abstractproperty


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(
        self, nome, data_nascimento, cpf, endereco, numero, bairro, cidade, telefone
    ):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.endereco = endereco
        self.numero = numero
        self.bairro = bairro
        self.cidadde = cidade
        self.telefone = telefone


class Conta:
    def __init__(self, numero, cliente, cpf):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._cpf = cpf
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero, cpf):
        return cls(numero, cliente, cpf)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def cpf(self):
        return self._cpf

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\tSaldo insuficiente!!!")

        elif valor > 0:
            self._saldo -= valor
            print("\t**** Saque realizado com sucesso! ****")
            return True

        else:
            print("\tO valor informado não pode ser [Negativo]")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\t**** Depósito realizado com sucesso! ****")

        else:
            print("\tO valor informado não pode ser [Negativo]")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, cpf, limite=600, limite_saques=3):
        super().__init__(numero, cliente, cpf)
        self.limite = limite
        self.limite_saques = limite_saques
        self.deposito = Deposito

    def sacar(self, valor):
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("\tLimite para Saque Excedido!!!")

        elif excedeu_saques:
            print("\tNúmero máximo de saques excedido!!!")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
        
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Cliente:\t{self.cliente.nome}
            CPF:\t\t{self.cpf}
           
          
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                #  "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = """
    ================ MENU ================
    [1]Depositar
    [2]Sacar
    [3]Extrato
    [4]Abrir conta
    [5]Exibir contas
    [6]Cadastrar Cliente
    [7]Sair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\t>>>Cliente não encontrado, Tente Novamente.<<<")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("\n>>> Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\t>>> Cliente não encontrado, Tente Novamente. <<<")
        return

    valor = float(input(">>> Informe o valor do depósito R$:"))

    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("\n>>> Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\t>>> Cliente não encontrado, Tente Novamente.<<<")
        return

    valor = float(input(">>> Informe o valor do saque R$:"))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input(">>> Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\t>>> Cliente não encontrado, Tente Novamente.<<<")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n************* EXTRATO *************")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n\n{transacao['tipo']}:\nR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo: R$ {conta.saldo:.2f}")


def cadastrar_cliente(clientes):
    cpf = input("Digite o CPF (somente número):")

    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\tEste CPF Já est cadastrado!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    endereco = input("Informe o endereço (Rua): ")
    numero = input("Número da Residência: ")
    bairro = input("Bairro: ")
    cidade = input("Cidade / Sigla do Estado: ")
    telefone = input("Telefone[(xx)xxxxx-xxxx]: ")

    cliente = PessoaFisica(
        nome=nome,
        data_nascimento=data_nascimento,
        cpf=cpf,
        endereco=endereco,
        numero=numero,
        bairro=bairro,
        cidade=cidade,
        telefone=telefone,
    )

    clientes.append(cliente)

    print("\t**** Cliente cadastrado com sucesso! ****")


def criar_conta(numero_conta, clientes, contas):
    cpf = input(">>> Digite o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\t>>> Cliente não encontrado, Tente Novamente. <<<")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, cpf=cpf, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\t**** Conta criada com sucesso! ****")


def exibir_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "5":
            exibir_contas(contas)

        elif opcao == "6":
            cadastrar_cliente(clientes)

        elif opcao == "7":
            print("\tDeseja Finalizar a Operação?")
            print("\t[s]=SIM / [n]=NÃO")

        if opcao == (f"{'s'}"):
            print("\n**** Operação Finalizada! ****")

        if opcao == (f"{'n'}"):
            print("**** Escolha a opção desejada ****")


main()
