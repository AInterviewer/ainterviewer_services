from domain import utils


def test_encrypt_message():
    test_message = "test"
    encrypted = utils.encrypt_message(test_message)

    assert test_message != encrypted
    assert isinstance(encrypted, bytes)


def test_decrypt_message():
    test_encrypted_message = b'gAAAAABj92osXKmDBunGsLGzn6aQegpg-kZ8TS18HExshJqlQ16BJNVKPFI3AUlluc1Y1BvmTnnLcXORqcp' \
                             b'D6U7uwp7ZMHdFfA=='
    decrypted = utils.decrypt_message(test_encrypted_message)

    assert test_encrypted_message != decrypted
    assert isinstance(decrypted, str)
