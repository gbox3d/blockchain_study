# blockchain.py
import time
from block import Block, BlockWithProof, Transaction

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []  # 아직 블록에 담지 않은 트랜잭션 목록
        self.mining_reward = 50  # 블록 채굴 시 보상 (가상화폐 발행 개념 예시)

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), [], "0")  # 제네시스 블록은 트랜잭션 없음
        genesis_block.set_hash()
        return genesis_block

    def get_latest_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def add_transaction(self, transaction):
        # 트랜잭션 유효성 체크
        if not transaction.is_valid():
            print("Invalid transaction. Not added.")
            return False
        self.pending_transactions.append(transaction)
        return True

    def create_block_from_pending(self):
        # 대기중인 트랜잭션을 담은 블록을 생성하고 체인에 추가
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions[:],  # 복사
            previous_hash=self.get_latest_block().hash
        )
        new_block.set_hash()
        self.chain.append(new_block)
        self.pending_transactions = []  # 대기중인 트랜잭션 초기화
        return new_block


class BlockchainWithPoW(Blockchain):
    def __init__(self, difficulty=4):
        super().__init__()
        self.difficulty = difficulty

    def create_block_from_pending(self, miner_address):
        # 대기중인 트랜잭션을 담은 BlockWithProof 생성
        # 채굴 보상을 위한 트랜잭션 추가 (miner_address에 보상 지급)
        reward_tx = Transaction("System", miner_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)

        new_block = BlockWithProof(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions[:],
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty
        )

        # 채굴
        new_block.mine_block()

        self.chain.append(new_block)
        self.pending_transactions = []  # 대기중 트랜잭션 초기화
        return new_block
