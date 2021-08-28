class Block:
    # def check_validity(self, prev_block, lite=True, blockchain=None) -> bool:
        # """
		# :param prev_block:
		# :param lite: Whether the client is Lite or not (Client or Miner).
		# :argument blockchain: Blockchain must be provided if checking for non-lite validity.
		# :return: Whether the block is valid or not
		# """
        # if not isinstance(prev_block, Block):
        #     return False
        # elif prev_block.index + 1 != self.index:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (BLOCK ORDER)')
        #     return False
        # elif prev_block.calculate_hash() != self.previous_block_hash:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (HASH)')
        #     return False
        # elif len(self.verified_transactions) == 0 and self.index != 0:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (NO VERIFIED TRANSACTIONS)')
        #     return False
        # elif self.timestamp <= prev_block.timestamp:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (TIMESTAMP)')
        #     return False
        # elif not verify_proof(prev_block.proof, self.proof):
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (PROOF)')
        #     return False
        # elif not self._verify_coinbase(lite=True):  # Lite verification of coinbase (No need to check each transaction)
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (COINBASE LITE)')
        #     return False
        # else:
        #     if not lite:
        #         # Verify each transaction that is valid
        #         for indx in range(0, len(self.verified_transactions)):
        #             trans = self.verified_transactions[indx]
        #             is_coinbase = True if indx == 0 else False
        #             if not trans.check_validity(blockchain=blockchain, is_coinbase=is_coinbase):
        #                 log.debug(f'[BLOCK - {self.hash}] Verification Failure (TRANSACTION INVALID)')
        #                 return False
        #
        #         if not self._verify_coinbase(lite=True):
        #             log.debug(f'[BLOCK - {self.hash}] Verification Failure (COINBASE)')
        #             return False
        #
        #     return True
x
