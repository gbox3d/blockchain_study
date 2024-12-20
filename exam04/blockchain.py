# blockchain.py
import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def is_valid(self):
        return self.amount > 0

    def __repr__(self):
        return f"Transaction({self.sender} -> {self.receiver}, {self.amount})"


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = None

    def calculate_hash(self):
        tx_str = "".join([f"{t.sender}{t.receiver}{t.amount}" for t in self.transactions])
        block_string = f"{self.index}{self.timestamp}{tx_str}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def set_hash(self):
        self.hash = self.calculate_hash()


class BlockWithProof(Block):
    def __init__(self, index, timestamp, transactions, previous_hash, difficulty=3):
        super().__init__(index, timestamp, transactions, previous_hash)
        self.nonce = 0
        self.difficulty = difficulty

    def calculate_hash(self):
        tx_str = "".join([f"{t.sender}{t.receiver}{t.amount}" for t in self.transactions])
        block_string = f"{self.index}{self.timestamp}{tx_str}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        prefix = "0" * self.difficulty
        while True:
            hashed = self.calculate_hash()
            if hashed.startswith(prefix):
                self.hash = hashed
                break
            self.nonce += 1


class BlockchainWithPoW:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.mining_reward = 50

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), [], "0")
        genesis_block.set_hash()
        return genesis_block

    def get_latest_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != prev_block.hash:
                return False
        return True

    def add_transaction(self, transaction):
        if transaction.is_valid():
            self.pending_transactions.append(transaction)
            return True
        return False

    def add_block(self, block):
        # 블록 체인에 추가 시 검증
        block.previous_hash = self.get_latest_block().hash
        if isinstance(block, BlockWithProof):
            # 블록이 이미 채굴되어 해시가 세팅되어 있어야 함
            # 여기서는 단순 검사만
            if not block.hash or block.hash != block.calculate_hash():
                return False
        else:
            block.set_hash()

        self.chain.append(block)
        return True

    def mine_pending_transactions(self, miner_address, difficulty=3):
        block = BlockWithProof(len(self.chain), time.time(), self.pending_transactions[:], self.get_latest_block().hash, difficulty)
        block.mine_block()
        self.chain.append(block)
        # 보상 트랜잭션
        self.pending_transactions = [Transaction("System", miner_address, self.mining_reward)]
        return block
