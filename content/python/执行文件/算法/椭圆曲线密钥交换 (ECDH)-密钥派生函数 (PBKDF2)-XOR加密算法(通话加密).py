import random
import hashlib
import secrets
import base64

class SimpleEllipticCurve:
    """简化的椭圆曲线类"""
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
    
    def point_add(self, P, Q):
        if P is None: return Q
        if Q is None: return P
        
        x1, y1 = P
        x2, y2 = Q
        
        if x1 == x2:
            if y1 != y2: return None
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
            inv_denominator = pow(denominator, self.p - 2, self.p)
            m = (numerator * inv_denominator) % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
            inv_denominator = pow(denominator, self.p - 2, self.p)
            m = (numerator * inv_denominator) % self.p
        
        x3 = (m * m - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        return (x3, y3)
    
    def point_multiply(self, k, P):
        if k % self.p == 0 or P is None: return None
        result = None
        addend = P
        while k:
            if k & 1: result = self.point_add(result, addend)
            addend = self.point_add(addend, addend)
            k >>= 1
        return result

class SecureMessagingDemo:
    def __init__(self):
        self.curve = SimpleEllipticCurve(a=2, b=2, p=17)
        self.G = (5, 1)  # 公共生成点
    
    def generate_key_pair(self):
        private_key = random.randint(1, self.curve.p - 1)
        public_key = self.curve.point_multiply(private_key, self.G)
        return private_key, public_key
    
    def compute_shared_secret(self, my_private, their_public):
        print(f"    计算共享密钥: {my_private} × {their_public}")
        shared_point = self.curve.point_multiply(my_private, their_public)
        print(f"    椭圆曲线乘法结果: {shared_point}")
        return shared_point[0] if shared_point else None
    
    def derive_key(self, shared_secret, salt=b""):
        print(f"    使用共享密钥 {shared_secret} 派生加密密钥")
        if not salt: 
            salt = secrets.token_bytes(8)
            print(f"    生成随机盐值: {salt.hex()}")
        
        # 将共享密钥转换为字节
        shared_bytes = str(shared_secret).encode()
        print(f"    共享密钥字节: {shared_bytes}")
        
        # 使用PBKDF2算法派生密钥
        print("    使用PBKDF2-HMAC-SHA256算法派生密钥...")
        derived_key = hashlib.pbkdf2_hmac('sha256', shared_bytes, salt, 1000, 16)
        print(f"    派生出的加密密钥: {derived_key.hex()}")
        
        return derived_key, salt
    
    def xor_encrypt(self, message, key):
        print(f"\n    --- 加密算法开始 ---")
        print(f"    原始消息: '{message}'")
        
        # 1. 将消息转换为字节
        msg_bytes = message.encode('utf-8')
        print(f"    消息字节: {msg_bytes}")
        
        # 2. 扩展密钥以匹配消息长度
        extended_key = (key * (len(msg_bytes) // len(key) + 1))[:len(msg_bytes)]
        print(f"    扩展后的密钥: {extended_key.hex()}")
        
        # 3. 执行XOR加密
        print("    执行XOR加密操作:")
        encrypted = bytearray()
        for i, (m, k) in enumerate(zip(msg_bytes, extended_key)):
            encrypted_byte = m ^ k
            encrypted.append(encrypted_byte)
            print(f"      字节[{i}]: {m:02x} XOR {k:02x} = {encrypted_byte:02x}")
        
        encrypted_bytes = bytes(encrypted)
        print(f"    加密后的字节: {encrypted_bytes.hex()}")
        
        # 4. Base64编码以便传输
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode('ascii')
        print(f"    Base64编码结果: {encrypted_b64}")
        print(f"    --- 加密算法结束 ---")
        
        return encrypted_b64
    
    def xor_decrypt(self, encrypted_data, key):
        print(f"\n    --- 解密算法开始 ---")
        print(f"    收到的加密数据: {encrypted_data}")
        
        # 1. Base64解码
        encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
        print(f"    Base64解码后字节: {encrypted_bytes.hex()}")
        
        # 2. 扩展密钥以匹配密文长度
        extended_key = (key * (len(encrypted_bytes) // len(key) + 1))[:len(encrypted_bytes)]
        print(f"    扩展后的密钥: {extended_key.hex()}")
        
        # 3. 执行XOR解密
        print("    执行XOR解密操作:")
        decrypted = bytearray()
        for i, (e, k) in enumerate(zip(encrypted_bytes, extended_key)):
            decrypted_byte = e ^ k
            decrypted.append(decrypted_byte)
            print(f"      字节[{i}]: {e:02x} XOR {k:02x} = {decrypted_byte:02x}")
        
        decrypted_bytes = bytes(decrypted)
        print(f"    解密后的字节: {decrypted_bytes}")
        
        # 4. 将字节转换回字符串
        decrypted_message = decrypted_bytes.decode('utf-8')
        print(f"    最终解密消息: '{decrypted_message}'")
        print(f"    --- 解密算法结束 ---")
        
        return decrypted_message

def detailed_alice_bob_communication():
    """Alice和Bob的详细安全通信演示"""
    print("=== Alice和Bob的安全通信（详细算法流程） ===\n")
    
    crypto = SecureMessagingDemo()
    
    # 1. 密钥生成
    print("1. 密钥生成阶段")
    print("   Alice生成密钥对:")
    alice_private, alice_public = crypto.generate_key_pair()
    print(f"    私钥: {alice_private}")
    print(f"    公钥: {alice_public}")
    
    print("\n   Bob生成密钥对:")
    bob_private, bob_public = crypto.generate_key_pair()
    print(f"    私钥: {bob_private}")
    print(f"    公钥: {bob_public}")
    
    # 2. 公钥交换
    print("\n2. 公钥交换阶段")
    print("   Alice将自己的公钥发送给Bob")
    print("   Bob将自己的公钥发送给Alice")
    
    # 3. 密钥协商
    print("\n3. 密钥协商阶段")
    print("   Alice计算共享密钥:")
    alice_shared = crypto.compute_shared_secret(alice_private, bob_public)
    print(f"    结果: {alice_shared}")
    
    print("\n   Bob计算共享密钥:")
    bob_shared = crypto.compute_shared_secret(bob_private, alice_public)
    print(f"    结果: {bob_shared}")
    
    print(f"\n   验证: 共享密钥{'匹配' if alice_shared == bob_shared else '不匹配'}!")
    
    # 4. 派生加密密钥
    print("\n4. 派生加密密钥阶段")
    print("   Alice派生加密密钥:")
    alice_key, salt = crypto.derive_key(alice_shared)
    
    print("\n   Bob派生加密密钥:")
    bob_key, _ = crypto.derive_key(bob_shared, salt)
    
    print(f"\n   验证: 加密密钥{'匹配' if alice_key == bob_key else '不匹配'}!")
    
    return crypto, alice_key, bob_key, alice_private, bob_private, alice_public, bob_public

def detailed_message_exchange(crypto, alice_key, bob_key):
    """详细的消息交换过程"""
    print("\n5. 消息交换阶段")
    
    # Alice发送消息给Bob
    print("\n--- Alice发送消息给Bob ---")
    alice_message = "Hi Bob!"
    print(f"   Alice要发送的消息: '{alice_message}'")
    
    print("   Alice使用以下信息加密:")
    print(f"     - 消息: '{alice_message}'")
    print(f"     - 加密密钥: {alice_key.hex()}")
    
    encrypted_msg = crypto.xor_encrypt(alice_message, alice_key)
    print(f"\n   Alice通过网络发送加密消息: {encrypted_msg}")
    
    # Bob接收并解密消息
    print("\n--- Bob接收并处理消息 ---")
    print(f"   Bob收到加密消息: {encrypted_msg}")
    print("   Bob使用以下信息解密:")
    print(f"     - 加密消息: {encrypted_msg}")
    print(f"     - 加密密钥: {bob_key.hex()}")
    
    decrypted_msg = crypto.xor_decrypt(encrypted_msg, bob_key)
    print(f"\n   Bob成功解密消息: '{decrypted_msg}'")
    
    # Bob回复消息给Alice
    print("\n--- Bob回复消息给Alice ---")
    bob_reply = "Hello Alice!"
    print(f"   Bob要回复的消息: '{bob_reply}'")
    
    print("   Bob使用以下信息加密:")
    print(f"     - 消息: '{bob_reply}'")
    print(f"     - 加密密钥: {bob_key.hex()}")
    
    encrypted_reply = crypto.xor_encrypt(bob_reply, bob_key)
    print(f"\n   Bob通过网络发送加密回复: {encrypted_reply}")
    
    # Alice接收并解密回复
    print("\n--- Alice接收并处理回复 ---")
    print(f"   Alice收到加密回复: {encrypted_reply}")
    print("   Alice使用以下信息解密:")
    print(f"     - 加密消息: {encrypted_reply}")
    print(f"     - 加密密钥: {alice_key.hex()}")
    
    decrypted_reply = crypto.xor_decrypt(encrypted_reply, alice_key)
    print(f"\n   Alice成功解密回复: '{decrypted_reply}'")
    
    return True

def algorithm_explanation():
    """算法步骤详细解释"""
    print("\n" + "="*60)
    print("算法步骤详细解释")
    print("="*60)
    
    print("\n1. 椭圆曲线密钥交换 (ECDH)")
    print("   公式: 共享密钥 = 我的私钥 × 对方的公钥")
    print("   特性: 双方使用不同的私钥和对方的公钥，但能得到相同的共享密钥")
    
    print("\n2. 密钥派生函数 (PBKDF2)")
    print("   输入: 共享密钥 + 盐值")
    print("   输出: 固定长度的加密密钥")
    print("   过程: 多次迭代哈希函数，增加暴力破解难度")
    
    print("\n3. XOR加密算法")
    print("   公式: 密文字节 = 明文字节 XOR 密钥字节")
    print("   特性: 同样的操作可用于加密和解密")
    print("   示例:")
    print("     明文字节: 0100 1001 (字符 'I')")
    print("     密钥字节: 0110 1001 (密钥)")
    print("     XOR操作: 0100 1001 XOR 0110 1001 = 0010 0000")
    print("     密文字节: 0010 0000")
    print("     解密操作: 0010 0000 XOR 0110 1001 = 0100 1001")
    
    print("\n4. Base64编码")
    print("   目的: 将二进制数据转换为可安全传输的文本格式")
    print("   使用场景: 在文本协议中传输加密数据")

def information_summary(alice_private, bob_private, alice_public, bob_public, alice_key, bob_key):
    """信息汇总"""
    print("\n" + "="*60)
    print("通信双方拥有的信息总结")
    print("="*60)
    
    print("\nAlice拥有的信息:")
    print(f"  - 私钥 (保密): {alice_private}")
    print(f"  - Bob的公钥 (公开): {bob_public}")
    print(f"  - 加密密钥 (派生): {alice_key.hex()}")
    
    print("\nBob拥有的信息:")
    print(f"  - 私钥 (保密): {bob_private}")
    print(f"  - Alice的公钥 (公开): {alice_public}")
    print(f"  - 加密密钥 (派生): {bob_key.hex()}")
    
    print("\n公开交换的信息:")
    print(f"  - Alice的公钥: {alice_public}")
    print(f"  - Bob的公钥: {bob_public}")
    print("  - 所有加密后的消息")
    
    print("\n保密的信息:")
    print("  - 双方的私钥")
    print("  - 共享密钥")
    print("  - 加密密钥")

if __name__ == "__main__":
    # 详细通信演示
    crypto, alice_key, bob_key, alice_private, bob_private, alice_public, bob_public = detailed_alice_bob_communication()
    
    # 详细消息交换
    detailed_message_exchange(crypto, alice_key, bob_key)
    
    # 算法解释
    algorithm_explanation()
    
    # 信息汇总
    information_summary(alice_private, bob_private, alice_public, bob_public, alice_key, bob_key)
    
    print("\n" + "="*60)
    print("总结: 安全通信成功建立!")
    print("="*60)