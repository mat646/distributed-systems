import sys
import os
import Ice
import signal
import grpc
import random
import string
from threading import Thread
import threading

sys.path.append(os.path.abspath("./utils/out/proto"))

import exchange_pb2
import exchange_pb2_grpc

sys.path.append(os.path.abspath("./utils/out/ice"))

from BankSystem import *
from currency_rates import *


def run_exchange_conn(arg):
    channel = grpc.insecure_channel('localhost:50051')
    stub = exchange_pb2_grpc.ExchangeStub(channel)
    request = exchange_pb2.ExchangeRequest(currency_rates=arg)
    try:
        for response in stub.subscribeExchangeRate(request):
            currency_rates_print()
            currency_rates[response.currency] = response.ExchangeRate
    except Exception as e:
        print(e)


class InvalidAccountTypeExceptionI(InvalidAccountTypeException):
    pass


class InvalidCredentialsExceptionI(InvalidCredentialsException):
    pass


class CurrencyNotSupportedExceptionI(CurrencyNotSupportedException):
    pass


class AccountI(Account):
    def __init__(self, accountType, name, surname, pesel, password, income):
        self.accountType = accountType
        self.name = name
        self.surname = surname
        self.pesel = pesel
        self.password = password
        self.income = income
        self.balance = Balance(income.value + 100)

    def getAccountType(self, current):
        print(f'*** Query for {self.pesel} account type ***')
        return self.accountType

    def getAccountBalance(self, current):
        print(f'*** Query for {self.pesel} account balance ***')
        return self.balance


class AccountStandardI(AccountI, AccountStandard):
    def applyForCredit(self, currency, amount, period, current):
        raise InvalidAccountTypeExceptionI


class AccountPremiumI(AccountI, AccountPremium):
    def applyForCredit(self, currency, amount, period, current):
        if currency.value not in currencies:
            raise CurrencyNotSupportedExceptionI
        credit_value = currency_rates[currency.value] * amount.value
        print('*** Credit application has been accepted ***')
        return CreditEstimate(amount, Balance(credit_value))


class AccountFactoryI(AccountFactory):
    def __init__(self):
        self.accountMap = {}

    def createAccount(self, name, surname, pesel, income, current):
        password = Password('wed-' + random.choice(string.ascii_letters))
        if income.value > 1000:
            acc_type = AccountType.PREMIUM
            account = AccountPremiumI(acc_type, name, surname, pesel, password, income)
        else:
            acc_type = AccountType.STANDARD
            account = AccountStandardI(acc_type, name, surname, pesel, password, income)

        asm_id = str(pesel.value) + '_' + acc_type.name
        self.accountMap[str(pesel.value) + password.value] = asm_id

        current.adapter.add(account, Ice.stringToIdentity(asm_id))
        print(f'*** The account {asm_id} has been created ***')
        return AccountCreated(password, account.accountType)

    def obtainAccess(self, pesel, current):
        try:
            asm_id = self.accountMap[str(pesel.value) + current.ctx['password']]
            acc_prx = AccountPrx.checkedCast(current.adapter.createProxy(Ice.stringToIdentity(asm_id)))
        except Exception:
            raise InvalidCredentialsExceptionI
        else:
            print(f'*** Access to {asm_id} has been obtained ***')
            return acc_prx


def exit_bank(signum, frame):
    for th in threading.enumerate():
        if th.is_alive():
            th._stop()
    communicator.shutdown()


with Ice.initialize(sys.argv, sys.argv[1]) as communicator:
    if __name__ == "__main__":
        currencies = list(map(lambda e: int(e), sys.argv[2:]))
        exchange_thread = Thread(target=run_exchange_conn, args=(currencies,))
        exchange_thread.start()

    signal.signal(signal.SIGINT, exit_bank)
    adapter = communicator.createObjectAdapter("BankObjectAdapter")
    adapter.add(AccountFactoryI(), Ice.stringToIdentity("accountFactory"))
    adapter.activate()
    print('*** The server is running ***')
    communicator.waitForShutdown()
