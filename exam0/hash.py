#%%
import hashlib

# 해쉬의 정의 : 해시는 임의의 길이의 데이터를 고정된 길이의 데이터로 매핑하는 함수이다.


# 간단한 예제
data = "Hello, Blockchain!"
hash_object = hashlib.sha256(data.encode())
print(f"SHA-256 Hash: {hash_object.hexdigest()}")
# %%
