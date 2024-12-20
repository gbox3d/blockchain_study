#%%
from blockchain import Blockchain, Block
import time

#%%
# 예제 블록 생성
genesis_block = Block(0, time.time(), "Genesis Block", "0")
print(f"Block #0 Hash: {genesis_block.hash}")


# %%

# 블록체인 초기화 및 블록 추가
my_blockchain = Blockchain()
my_blockchain.add_block(Block(1, time.time(), "Block 1 Data", ""))
my_blockchain.add_block(Block(2, time.time(), "Block 2 Data", ""))

# 블록체인 출력
for block in my_blockchain.chain:
    print(f"Block #{block.index}, Hash: {block.hash},   Hash: {block.previous_hash}")

# %%

print(my_blockchain.is_chain_valid())
# %%
