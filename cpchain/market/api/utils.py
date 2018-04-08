import hashlib
import logging
import random

from cpchain.crypto import SHA256Hash, ECCipher

logger = logging.getLogger(__name__)


def md5(source):
    digest = hashlib.md5()
    digest.update(source)
    return digest.hexdigest()


def sha256(s):
    digest_string = SHA256Hash.generate_hash(s)
    print(digest_string)
    return digest_string


def generate_random_str(randomlength=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def is_valid_signature(public_key, raw_data, signature):
    # TODO verify signature of public_key+verify_code
    print("is_valid_verify_code public_key:" + public_key + ",raw_data:" + raw_data + ",signature:" + signature)
    return verify_signature(public_key, signature, raw_data)


def generate_signature(pri_key_string, raw_data, password=None):
    return sign(pri_key_string=pri_key_string, raw_data=raw_data, password=password)


def generate_msg_hash(msg_hash_source):
    return SHA256Hash.generate_hash(msg_hash_source)


def generate_keys():
    # return ECCipher.generate_keys()
    return ECCipher.generate_der_keys()


def verify_signature(pub_key_string, signature, raw_data):
    return ECCipher.verify_der_signature(pub_key_string=pub_key_string, signature=signature, raw_data_string=raw_data)


def sign(pri_key_string, raw_data):
    return ECCipher.sign_der(pri_key_string, raw_data)



if __name__ == '__main__':
    sample = "qZaQ6S"
    private_key_string, public_key_string = generate_keys()

    private_key_string="MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ="
    public_key_string="MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g=="


    print("pri key:" + private_key_string)
    print("pub key:" + public_key_string)

    print("================ppk:")
    print(private_key_string)
    print("sample:")
    print(sample)
    new_signature = sign(private_key_string, sample)
    print("111 new_signature is:")
    print(new_signature)

    is_valid_sign = verify_signature(public_key_string, new_signature, sample)
    print("111 is valid new_signature:" + str(is_valid_sign))


    new_signature = sign(private_key_string, sample)
    print("222 new_signature is:")
    print(new_signature)


    is_valid_sign = verify_signature(public_key_string, new_signature, sample)
    print("222 is valid new_signature:" + str(is_valid_sign))

    print("================ppk:")

    # confirm verify code
    # pri key:MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ=
    # pub key:MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g==
    # data:qZaQ6S
    # sign:MEQCIFr0iMsvk2jP95G5f8oUM8cw8fA7ZQyXxNWVNoPFIHQeAiB5oir5ljU1a580YxXLHGVtbSkZWCjZo7cD2fWharOouw==
    # piks = "MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAgjM93unpf4KgICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEDNQSMFCdUeLf2+9qd3CFl0EgZCycmt0ZehvfWd5topy0pXuW4ehL2ign4SW4Jl+Jfo1YezBDs3PvLqqDpfMk3PMEtaeVxUE51WBZbDHNmjmP8bmkdunlVQNYUybQLWpBt0DFX9b2F0yR0qjoyGH1JJlqPEjV4FvhbCI7SJyF6raocl09DZCAy+lu71L3jTZOraUUbxH9VHUatbOH7B/qyjhmSE="
    # puks = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEVWPo4T5VbYn391ZahHf9HgjRsox6k3Kix7HP4PbIWlOvkQ9KZFMHk34PoMNircsbC4FysZKVbAl8ENFVf2GyDA=="
    # data = "qZaQ6S"
    # new_signature = sign(piks, data)
    # print("++++ 1 new code signature is:" + new_signature)

    # expected_sign = "MEYCIQC2U2WoOsxew+E9Hy0rTg6+Rh8v3GNsnpXMGdJ9/sBLcAIhAKCbAPhwqJP86DjVMibg5rNU4pYABEf2JD5GBLSC4OGJ"

    # publish data signature
    # piks="MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ="
    # puks="MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g=="
    piks="MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ="
    puks="MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g=="

    data = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g==6666677881224152254861015225486101234567890"

    # "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g==6666677881224152254861015225486101234567890"
    new_signature = sign(piks, data)
    print("++++ 2 new_signature is:" + new_signature)

    # new_signature = "MEUCIHANJeMdqDOb6y5gSijqxTbgDeHIF2FJMtgGJPHPm6SSAiEAlVBnYKsN9l/ahc6cxTtGTJxdxM0P6lnFt4pjmFgsBLA="
    is_valid_sign = verify_signature(puks, new_signature, data)
    print("is valid new_signature:" + str(is_valid_sign))
