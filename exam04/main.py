# main.py
import asyncio
import sys
import socket
from node import Node
from blockchain import Transaction

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <port> [<peer_host> <peer_port>]")
        return

    port = int(sys.argv[1])
    # 실제 IP 주소 얻기 (LAN IP)
    real_ip = socket.gethostbyname(socket.gethostname())

    node = Node(host=real_ip, port=port)

    # 피어와 연결(옵션)
    if len(sys.argv) == 4:
        peer_host = sys.argv[2]
        peer_port = int(sys.argv[3])
        await node.connect_to_peer(peer_host, peer_port)

    # 노드 서버 시작
    asyncio.create_task(node.start_server())

    print(f"Node running at {real_ip}:{port}")

    loop = asyncio.get_event_loop()
    while True:
        print("Commands: addtx sender receiver amount | mine minerAddress | exit")
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        cmd = line.strip().split()
        if cmd[0] == "addtx":
            if len(cmd) != 4:
                print("Usage: addtx <sender> <receiver> <amount>")
                continue
            sender, receiver, amount = cmd[1], cmd[2], float(cmd[3])
            t = Transaction(sender, receiver, amount)
            node.blockchain.add_transaction(t)
            msg = {"type": "new_transaction", "transaction": {"sender": sender, "receiver": receiver, "amount": amount}}
            await node.broadcast_message(msg)
            print("Transaction added and broadcasted.")

        elif cmd[0] == "mine":
            if len(cmd) != 2:
                print("Usage: mine <minerAddress>")
                continue
            miner_address = cmd[1]
            # mine_pending_transactions는 이제 async 함수이므로 await 사용
            await node.mine_pending_transactions(miner_address)


        elif cmd[0] == "exit":
            print("Exiting node...")
            break
        else:
            print("Unknown command")

if __name__ == "__main__":
    asyncio.run(main())
