import random

class SimpleEllipticCurve:
    """一个简化的椭圆曲线类，用于演示基本原理"""
    
    def __init__(self, a, b, p):
        """
        初始化椭圆曲线: y² = x³ + ax + b (mod p)
        """
        self.a = a
        self.b = b
        self.p = p  # 有限域的模
    
    def is_on_curve(self, point):
        """检查点是否在曲线上"""
        if point is None:  # 无穷远点
            return True
        x, y = point
        return (y * y) % self.p == (x * x * x + self.a * x + self.b) % self.p
    
    def point_add(self, P, Q):
        """椭圆曲线点加法"""
        if P is None:
            return Q
        if Q is None:
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        if x1 == x2:
            if y1 != y2:  # P + (-P) = 无穷远点
                return None
            else:  # P == Q，点加倍
                # 斜率 m = (3x₁² + a) / (2y₁) mod p
                numerator = (3 * x1 * x1 + self.a) % self.p
                denominator = (2 * y1) % self.p
                # 求分母的模逆元
                inv_denominator = pow(denominator, self.p - 2, self.p)
                m = (numerator * inv_denominator) % self.p
        else:
            # 斜率 m = (y₂ - y₁) / (x₂ - x₁) mod p
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
            # 求分母的模逆元
            inv_denominator = pow(denominator, self.p - 2, self.p)
            m = (numerator * inv_denominator) % self.p
        
        # 计算新点的坐标
        x3 = (m * m - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def point_multiply(self, k, P):
        """椭圆曲线标量乘法: k * P"""
        if k % self.p == 0 or P is None:
            return None
        
        # 使用倍加算法
        result = None
        addend = P
        
        while k:
            if k & 1:  # 如果当前位是1
                result = self.point_add(result, addend)
            addend = self.point_add(addend, addend)  # 点加倍
            k >>= 1  # 移到下一位
        
        return result

class SimpleBitcoinDemo:
    """简化的比特币密钥生成演示"""
    
    def __init__(self):
        # 使用一个小型的椭圆曲线参数进行演示
        # 真实比特币使用 secp256k1 曲线，参数大得多
        self.curve = SimpleEllipticCurve(a=2, b=2, p=17)
        
        # 选择一个生成点 (这个点在曲线上)
        self.G = (5, 1)  # 生成点/基准点
        
        # 验证生成点确实在曲线上
        if not self.curve.is_on_curve(self.G):
            raise ValueError("生成点不在曲线上!")
    
    def generate_keys(self):
        """生成私钥和公钥"""
        # 私钥: 一个随机数 (在真实系统中，这是一个256位的随机数)
        private_key = random.randint(1, self.curve.p - 1)
        
        # 公钥: private_key * G (椭圆曲线乘法)
        public_key = self.curve.point_multiply(private_key, self.G)
        
        return private_key, public_key
    
    def demo_signature(self, private_key, message_hash):
        """简化的签名演示 (实际签名算法更复杂)"""
        # 在实际ECDSA中，这里会涉及更多的步骤
        # 这里我们只做一个简化的演示
        
        # 选择一个临时密钥 (在实际中必须是随机的)
        k = random.randint(1, self.curve.p - 1)
        
        # 计算 R = k * G
        R = self.curve.point_multiply(k, self.G)
        r = R[0] % self.curve.p  # 取x坐标
        
        # 简化的签名计算 (实际ECDSA更复杂)
        # s = (message_hash + private_key * r) / k mod p
        inv_k = pow(k, self.curve.p - 2, self.curve.p)
        s = ((message_hash + private_key * r) * inv_k) % self.curve.p
        
        return (r, s)
    
    def verify_signature(self, public_key, message_hash, signature):
        """简化的签名验证演示"""
        r, s = signature
        
        # 验证签名有效性
        if r < 1 or r >= self.curve.p or s < 1 or s >= self.curve.p:
            return False
        
        # 计算 w = s^(-1) mod p
        w = pow(s, self.curve.p - 2, self.curve.p)
        
        # 计算 u1 = message_hash * w mod p
        u1 = (message_hash * w) % self.curve.p
        
        # 计算 u2 = r * w mod p
        u2 = (r * w) % self.curve.p
        
        # 计算点 P = u1 * G + u2 * public_key
        P1 = self.curve.point_multiply(u1, self.G)
        P2 = self.curve.point_multiply(u2, public_key)
        P = self.curve.point_add(P1, P2)
        
        if P is None:
            return False
        
        # 验证 P 的 x 坐标是否等于 r mod p
        return P[0] % self.curve.p == r

def main():
    """主演示函数"""
    print("=== 简化的椭圆曲线加密演示 ===\n")
    
    # 创建演示实例
    demo = SimpleBitcoinDemo()
    
    print("1. 生成密钥对")
    private_key, public_key = demo.generate_keys()
    print(f"   私钥 (秘密数字): {private_key}")
    print(f"   公钥 (曲线上的点): {public_key}")
    print(f"   验证公钥在曲线上: {demo.curve.is_on_curve(public_key)}\n")
    
    print("2. 演示椭圆曲线运算")
    # 展示 2 * G
    point_2G = demo.curve.point_multiply(2, demo.G)
    print(f"   2 * G = {point_2G}")
    print(f"   验证 2G 在曲线上: {demo.curve.is_on_curve(point_2G)}")
    
    # 展示 3 * G = G + 2G
    point_3G_1 = demo.curve.point_multiply(3, demo.G)
    point_3G_2 = demo.curve.point_add(demo.G, point_2G)
    print(f"   3 * G = {point_3G_1}")
    print(f"   G + 2G = {point_3G_2}")
    print(f"   两者相等: {point_3G_1 == point_3G_2}\n")
    
    print("3. 简化的签名演示")
    message_hash = 7  # 简化的消息哈希值
    signature = demo.demo_signature(private_key, message_hash)
    print(f"   消息哈希: {message_hash}")
    print(f"   签名 (r, s): {signature}")
    
    # 验证签名
    is_valid = demo.verify_signature(public_key, message_hash, signature)
    print(f"   签名验证: {'成功' if is_valid else '失败'}")
    
    # 尝试用错误的公钥验证
    _, wrong_public_key = demo.generate_keys()
    is_valid_wrong = demo.verify_signature(wrong_public_key, message_hash, signature)
    print(f"   错误公钥验证: {'错误地成功' if is_valid_wrong else '正确地失败'}\n")
    
    print("4. 重要说明")
    print("   - 这是一个极度简化的演示，使用非常小的参数")
    print("   - 真实比特币使用 secp256k1 曲线，模数 p ≈ 2²⁵⁶")
    print("   - 真实私钥是 256 位随机数，约 10⁷⁷ 种可能")
    print("   - 实际攻击几乎不可能通过公钥反推私钥")

if __name__ == "__main__":
    main()