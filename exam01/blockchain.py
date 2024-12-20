#%%
import hashlib
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    

    
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
#%%
if __name__ == "__main__":
    blockchain = Blockchain()
    block1 = Block(1, time.time(), "Block 1", "")
    blockchain.add_block(block1)
    block2 = Block(2, time.time(), "Block 2", "")
    blockchain.add_block(block2)
    block3 = Block(3, time.time(), "Block 3", "")
    blockchain.add_block(block3)
    
        
    # 블록체인 출력
    for block in blockchain.chain:
        print(f"Block #{block.index}, Hash: {block.hash}, Previous Hash: {block.previous_hash}")

    
    print(blockchain.is_chain_valid())
# %%
