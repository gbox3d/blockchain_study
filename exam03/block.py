# block.py
import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def is_valid(self):
        # 간단한 검증: 금액이 양수인지 확인
        return self.amount > 0

    def __repr__(self):
        return f"Transaction(from={self.sender}, to={self.receiver}, amount={self.amount})"


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        # data 대신 transactions 리스트를 사용
        self.transactions = transactions  # 리스트 형태
        self.previous_hash = previous_hash
        self.hash = None  # 해시는 set_hash()에서 계산

    def calculate_hash(self):
        # 트랜잭션 리스트를 문자열로 변환
        tx_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}" for tx in self.transactions])
        block_string = f"{self.index}{self.timestamp}{tx_str}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def set_hash(self):
        self.hash = self.calculate_hash()


class BlockWithProof(Block):
    def __init__(self, index, timestamp, transactions, previous_hash, difficulty=4):
        super().__init__(index, timestamp, transactions, previous_hash)
        self.nonce = 0
        self.difficulty = difficulty

    def calculate_hash(self):
        tx_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}" for tx in self.transactions])
        block_string = f"{self.index}{self.timestamp}{tx_str}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        prefix = "0" * self.difficulty
        while True:
            calculated_hash = self.calculate_hash()
            if calculated_hash.startswith(prefix):
                self.hash = calculated_hash
                break
            self.nonce += 1
