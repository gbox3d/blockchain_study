# node.py
import asyncio
import json
from blockchain import BlockchainWithPoW, Transaction, BlockWithProof, Block

class Node:
    def __init__(self, host='127.0.0.1', port=5000, difficulty=3):
        self.host = host
        self.port = port
        self.blockchain = BlockchainWithPoW()
        self.peers = set()  # 다른 노드 주소 (host:port) 집합
        self.difficulty = difficulty

    async def start_server(self):
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        print(f"Node started on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            await self.handle_message(message, writer)
        writer.close()

    async def handle_message(self, message, writer):
        # 메시지(JSON) 파싱
        try:
            msg = json.loads(message)
        except:
            return
        msg_type = msg.get("type")

        if msg_type == "new_block":
            # 다른 노드가 채굴한 블록
            block_data = msg["block"]
            block = BlockWithProof(
                block_data["index"],
                block_data["timestamp"],
                [Transaction(t["sender"], t["receiver"], t["amount"]) for t in block_data["transactions"]],
                block_data["previous_hash"],
                difficulty=block_data["difficulty"]
            )
            block.nonce = block_data["nonce"]
            block.hash = block_data["hash"]

            # 블록 추가 시도
            if self.blockchain.add_block(block):
                print(f"Received new block #{block.index} from network")
            else:
                print("Received invalid block")

        elif msg_type == "chain_request":
            # 체인 요청 -> 현재 체인 전송
            chain_data = [self.block_to_dict(b) for b in self.blockchain.chain]
            response = {"type": "chain_response", "chain": chain_data}
            writer.write((json.dumps(response) + "\n").encode())
            await writer.drain()

        elif msg_type == "chain_response":
            # 다른 노드의 체인 수신
            chain_data = msg["chain"]
            # 간단히 체인 길이가 더 길면 교체
            if len(chain_data) > len(self.blockchain.chain):
                new_chain = []
                for b in chain_data:
                    if "nonce" in b:
                        block = BlockWithProof(
                            b["index"], b["timestamp"],
                            [Transaction(t["sender"], t["receiver"], t["amount"]) for t in b["transactions"]],
                            b["previous_hash"], difficulty=b["difficulty"]
                        )
                        block.nonce = b["nonce"]
                        block.hash = b["hash"]
                    else:
                        block = Block(
                            b["index"], b["timestamp"],
                            [Transaction(t["sender"], t["receiver"], t["amount"]) for t in b["transactions"]],
                            b["previous_hash"]
                        )
                        block.hash = b["hash"]
                    new_chain.append(block)
                # 교체
                # 실제 구현에서는 유효성 검사 필요
                self.blockchain.chain = new_chain
                print("Replaced chain with received chain")

        elif msg_type == "new_transaction":
            # 새로운 트랜잭션
            t = msg["transaction"]
            tx = Transaction(t["sender"], t["receiver"], t["amount"])
            added = self.blockchain.add_transaction(tx)
            if added:
                print(f"Transaction added: {tx}")
            else:
                print("Invalid transaction")

        elif msg_type == "add_peer":
            # 새로운 피어 추가
            peer = msg["peer"]
            self.peers.add(peer)
            print(f"New peer added: {peer}")

    def block_to_dict(self, block):
        d = {
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": [{"sender": t.sender, "receiver": t.receiver, "amount": t.amount} for t in block.transactions],
            "previous_hash": block.previous_hash,
            "hash": block.hash
        }
        if isinstance(block, BlockWithProof):
            d["nonce"] = block.nonce
            d["difficulty"] = block.difficulty
        return d

    async def connect_to_peer(self, peer_host, peer_port):
        # 피어에 연결 -> 피어 리스트에 추가
        self.peers.add(f"{peer_host}:{peer_port}")
        reader, writer = await asyncio.open_connection(peer_host, peer_port)
        # 피어에게 나 자신 추가 요청
        msg = {"type": "add_peer", "peer": f"{self.host}:{self.port}"}
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()
        writer.close()

    async def broadcast_block(self, block):
        # 새 블록을 모든 피어에게 전송
        block_data = self.block_to_dict(block)
        msg = {"type": "new_block", "block": block_data}
        await self.broadcast_message(msg)

    async def broadcast_message(self, msg):
        for p in list(self.peers):
            host, port = p.split(":")
            try:
                reader, writer = await asyncio.open_connection(host, int(port))
                writer.write((json.dumps(msg) + "\n").encode())
                await writer.drain()
                writer.close()
            except:
                pass

    # def mine_pending_transactions(self, miner_address):
    #     block = self.blockchain.mine_pending_transactions(miner_address, difficulty=self.difficulty)
    #     # 채굴 완료 시 블록 브로드캐스트 필요
    #     asyncio.run(self.broadcast_block(block))
    #     print(f"Mined block #{block.index}, broadcasted to peers.")
    
    async def mine_pending_transactions(self, miner_address):
        block = self.blockchain.mine_pending_transactions(miner_address, difficulty=self.difficulty)
        # 채굴 완료 시 블록 브로드캐스트를 await로 비동기 호출
        await self.broadcast_block(block)
        print(f"Mined block #{block.index}, broadcasted to peers.")


    async def request_chain(self, peer_host, peer_port):
        # 다른 노드의 체인 요청
        reader, writer = await asyncio.open_connection(peer_host, peer_port)
        msg = {"type": "chain_request"}
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()

        data = await reader.readline()
        if data:
            response = json.loads(data.decode().strip())
            if response["type"] == "chain_response":
                print("Received chain:", response["chain"])
        writer.close()
