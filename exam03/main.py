#%% main.py
from blockchain import Blockchain, BlockchainWithPoW, Transaction
import time

#%%
if __name__ == "__main__":
    # 기본 블록체인 예제
    bc = Blockchain()
    # 트랜잭션 추가
    bc.add_transaction(Transaction("Alice", "Bob", 10))
    bc.add_transaction(Transaction("Bob", "Charlie", 20))

    # 대기중인 트랜잭션으로 블록 생성
    bc.create_block_from_pending()

    for block in bc.chain:
        print(f"[BasicChain] Block #{block.index}, Hash: {block.hash}, PrevHash: {block.previous_hash}")
        print("  Transactions:")
        for tx in block.transactions:
            print("   ", tx)
    print("Is BasicChain valid?", bc.is_chain_valid())


#%%
    # PoW 블록체인 예제
    pow_bc = BlockchainWithPoW(difficulty=3)
    pow_bc.add_transaction(Transaction("Alice", "Bob", 5))
    pow_bc.add_transaction(Transaction("Bob", "Charlie", 2))

    # 블록을 채굴(miner: "Miner1")
    pow_bc.create_block_from_pending("Miner1")

    pow_bc.add_transaction(Transaction("Charlie", "Dave", 1))
    pow_bc.create_block_from_pending("Miner1")

    # 블록체인 출력
    for block in pow_bc.chain:
        print(f"[PoWChain] Block #{block.index}, Nonce: {getattr(block, 'nonce', None)}, Hash: {block.hash}, PrevHash: {block.previous_hash}")
        print("  Transactions:")
        for tx in block.transactions:
            print("   ", tx)
    print("Is PoWChain valid?", pow_bc.is_chain_valid())
