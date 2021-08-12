from Crypto.Hash import SHA256


def verify_proof(prev_proof, proof, difficulty=2) -> bool:
    """
    Verifying if the Proof-of-Work is correct, based on a specific difficulty.
    :param prev_proof: Proof-of-Work of previous block.
    :param proof: Proof-of-Work that is to be checked.
    :param difficulty: Difficulty level that is to be checked.
    :return: Whether the Proof-of-Work found is valid or not.
    """
    if difficulty <= 0:
        raise ValueError("Difficulty must be a positive number!")

    guess = f'{prev_proof}{proof}'.encode()
    guess_hash = SHA256.new(guess).hexdigest()
    return guess_hash[:difficulty] == "1" * difficulty


def proof_of_work(prev_proof: int, difficulty=2) -> int:
    """
    Proof-of-Work algorithm. Increment a random number and trying to verify it
    each time until Proof-of-work returns True.
    :param prev_proof: Proof-of-Work of previous block.
    :param difficulty: Difficulty level of mining.
    :return:
    """
    proof = 0
    while verify_proof(prev_proof, proof, difficulty) is False:
        proof += 1

    return proof
