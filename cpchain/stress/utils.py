import os

from hashlib import sha1
from random import randint

from signal import signal, SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM

from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredList, inlineCallbacks

from cpchain.stress.account import create_test_accounts

def entropy(length):
    return "".join(chr(randint(0, 255)) for _ in range(length))

def random_id():
    h = sha1()
    h.update(entropy(10).encode('utf-8'))
    return h.digest().hex()

def signal_handler(*args):
    os._exit(0)

def install_signal():
    for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
        signal(sig, signal_handler)


players = {}
job_id = -1

@inlineCallbacks
def job_loop(loop_num, accounts, Player, job):
    global job_id

    job_id += 1

    test_players = []
    for account in accounts:
        if account in players:
            player = players[account]
        else:
            player = Player(account)
            players[account] = player

        test_players.append(player)

    seller = test_players[0]
    buyer = test_players[1]
    proxy = test_players[2]

    for i in range(0, loop_num):
        success = yield job(seller, buyer, proxy)
        if not success:
            print('job %d loop %d failure: seller %s, buyer %s, proxy %s' % (
                job_id, i, seller.address, buyer.address, proxy.address)
                )

            break
        else:
            print('job %d loop %d success : seller %s, buyer %s, proxy %s' % (
                job_id, i, seller.address, buyer.address, proxy.address)
                )

    return success

@inlineCallbacks
def run_jobs(Player, job, account_num=None, concurrence_num=None, loop_num=None):
    install_signal()

    account_num = account_num or 100
    concurrence_num = concurrence_num or 100
    loop_num = loop_num or 10

    ds = []

    accounts = yield create_test_accounts(account_num)

    while concurrence_num:
        test_accounts = []
        for i in range(0, 3):
            account = accounts[randint(0, account_num - 1)]
            test_accounts.append(account)

        d = job_loop(loop_num, test_accounts, Player, job)
        ds.append(d)

        concurrence_num -= 1

    def handle_result(result):
        success_num = 0
        failure_num = 0
        for (success, value) in result:
            if success:
                if value:
                    success_num += 1
                else:
                    failure_num += 1
            else:
                print('job failure with exception: %s' % value.getErrorMessage())
                failure_num += 1

        print('job stat: %d succeed, %d failed.' % (success_num, failure_num))

    if ds:
        dl = DeferredList(ds, consumeErrors=True)
        dl.addCallback(handle_result)
