import sys
import os
import Ice

sys.path.append(os.path.abspath("./utils/out/ice"))

from BankSystem import *

def cli_wr_rd(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
    return sys.stdin.readline().strip()

def run(communicator):
    server = AccountFactoryPrx.checkedCast(
        communicator.propertyToProxy('AccountFactory.Proxy').ice_twoway().ice_secure(False))
    if not server:
        print('invalid server proxy')
        sys.exit(1)

    account_proxy = None

    while True:
        if account_proxy is None:
            command = cli_wr_rd('bank-welcome$ ')
            if command == 'help':
                print('there is no help')
            elif command == 'signup':
                name = cli_wr_rd('your-name$ ')
                surname = cli_wr_rd('your-surname$ ')
                pesel = cli_wr_rd('your-pesel$ ')
                balance = cli_wr_rd('your-balance$ ')
                acc_create_resp = server.createAccount(Name(name),
                                                       Surname(surname),
                                                       Pesel(int(pesel)),
                                                       Balance(int(balance)))
                print(acc_create_resp)
            elif command == 'signin':
                pesel = cli_wr_rd('your-pesel$ ')
                password = cli_wr_rd('your-password$ ')
                try:
                    account_proxy = server.obtainAccess(Credentials(Pesel(int(pesel)), Password(password)))
                except InvalidCredentialsException as error:
                    print(error)
                else:
                    print(account_proxy)
            else:
                print('invalid command, use \'help\'')
        else:
            sys.stdout.write(f'bank-{account_proxy.getAccountType()}$ ')
            sys.stdout.flush()
            command = sys.stdin.readline().strip()
            if command == 'help':
                print('there is no help')
            elif command == 'signout':
                account_proxy = None
            elif command == 'balance':
                print(f'your balance is: {account_proxy.getAccountBalance()}')
            elif command == 'credit':
                credit_estimate = account_proxy.applyForCredit(Currency.PLN, Balance(1000), Period('6 months'))
                print(credit_estimate)
            elif command == 'accounttype':
                print(f'your account type is: {account_proxy.getAccountType()}')
            else:
                print('invalid command, use \'help\'')


with Ice.initialize(sys.argv, "./client/config.client") as communicator:
    run(communicator)
