#%% block.py
import hashlib
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = None  # 해시는 별도 메서드 호출로 설정할 것

    def calculate_hash(self):
        # 기본 블록은 nonce 없음
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def set_hash(self):
        self.hash = self.calculate_hash()


class BlockWithProof(Block):
    def __init__(self, index, timestamp, data, previous_hash, difficulty=4):
        super().__init__(index, timestamp, data, previous_hash)
        self.nonce = 0
        self.difficulty = difficulty
        # 여기서는 바로 mine_block()을 호출하지 않음
        # 필요 시 외부에서 mine_block() 혹은 set_hash()를 호출

    def calculate_hash(self):
        # nonce 포함
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        # 해시가 유효할 때까지 nonce를 증가
        prefix = "0" * self.difficulty
        while True:
            calculated_hash = self.calculate_hash()
            if calculated_hash.startswith(prefix):
                self.hash = calculated_hash
                break
            self.nonce += 1


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        # 제네시스 블록 생성 및 해시 설정
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        genesis_block.set_hash()
        return genesis_block

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        # 블록 추가 전 이전 해시 설정
        new_block.previous_hash = self.get_latest_block().hash
        # 여기서 해시가 이미 설정되어 있어야 함(Block 혹은 BlockWithProof에서 mine_block 또는 set_hash 수행)
        if new_block.hash is None:
            # 기본 Block이라면 그냥 set_hash 호출
            if isinstance(new_block, BlockWithProof):
                # BlockWithProof인데 hash가 없다면?
                # 외부에서 mine_block하지 않았다면 여기서 set_hash만 호출
                new_block.set_hash()
            else:
                new_block.set_hash()

        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 해시 확인
            if current_block.hash != current_block.calculate_hash():
                return False
            # 이전 해시 링크 확인
            if current_block.previous_hash != previous_block.hash:
                return False
        return True


class BlockchainWithPoW(Blockchain):
    def add_block(self, new_block):
        # 부모 체인과 달리 여기서는 블록 추가 전에 mine_block 수행 (BlockWithProof인 경우)
        if isinstance(new_block, BlockWithProof):
            # previous_hash 설정 후 mine
            new_block.previous_hash = self.get_latest_block().hash
            new_block.mine_block()
        else:
            # 혹시라도 BlockWithProof 아닌걸 넣는다면 그냥 hash 설정
            new_block.previous_hash = self.get_latest_block().hash
            new_block.set_hash()

        self.chain.append(new_block)

#%%

# 예제 실행 코드
if __name__ == "__main__":
    # 기본 블록체인 예제
    bc = Blockchain()
    block1 = Block(1, time.time(), "Block 1", "")
    block1.set_hash()
    bc.add_block(block1)

    block2 = Block(2, time.time(), "Block 2", "")
    block2.set_hash()
    bc.add_block(block2)

    for block in bc.chain:
        print(f"[BasicChain] Block #{block.index}, Hash: {block.hash}, PrevHash: {block.previous_hash}")
    print("Is BasicChain valid?", bc.is_chain_valid())


    # PoW 블록체인 예제
    pow_bc = BlockchainWithPoW()
    # mine_block 호출 전에는 hash 설정 없음
    # 시간 측정
    start_time = time.time()
    block_pow_1 = BlockWithProof(1, time.time(), "Block 1 Data", "", difficulty=4)
    pow_bc.add_block(block_pow_1)
    print(f"Elapsed Time: {time.time() - start_time:.4f}s")

    start_time = time.time()
    block_pow_2 = BlockWithProof(2, time.time(), "Block 2 Data", "", difficulty=4)
    pow_bc.add_block(block_pow_2)
    print(f"Elapsed Time: {time.time() - start_time:.4f}s")

    for block in pow_bc.chain:
        print(f"[PoWChain] Block #{block.index}, Nonce: {getattr(block, 'nonce', None)}, Hash: {block.hash}, PrevHash: {block.previous_hash}")
    print("Is PoWChain valid?", pow_bc.is_chain_valid())

# %%
