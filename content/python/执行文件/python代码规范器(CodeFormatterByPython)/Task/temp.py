# test_comprehensive_scope.py
"""
全面测试作用域相关的重命名问题
"""

# 全局变量
global_var = "global"
GlobalConstant = "constant"

def TestFunction():
    # 局部变量 - 与全局变量同名但不同作用域
    global_var = "local"
    
    # 使用global声明
    global GlobalConstant
    GlobalConstant = "modified"
    
    # 局部变量
    local_var = 10
    
    print(f"函数内部 global_var: {global_var}")
    print(f"函数内部 GLOBAL_CONSTANT: {GlobalConstant}")
    
    # 嵌套函数
    def InnerFunction():
        # 使用nonlocal
        nonlocal local_var
        local_var = 20
        
        # 内部函数变量
        inner_var = "inner"
        
        print(f"内部函数 inner_var: {inner_var}")
        print(f"内部函数 local_var: {local_var}")
    
    InnerFunction()
    return local_var

class TestClass1:
    # 类变量
    class_var = "class"
    
    def __init__1(self):
        # 实例变量 - 与类变量同名
        self.class_var = "instance"
        self.instance_var = "instance"
    
    def Method(self, param):
        # 方法参数
        method_var = "method"
        
        # 与实例变量同名
        instance_var = "local"
        
        print(f"方法中 param: {param}")
        print(f"方法中 method_var: {method_var}")
        print(f"方法中 instance_var: {instance_var}")
        print(f"方法中 self.instance_var: {self.instance_var}")
        
        # 列表推导式 - 有独立作用域
        result = [x for x in range(5)]
        print(f"列表推导式结果: {result}")
        
        return method_var

# 测试属性访问（不应被重命名）
obj = TestClass1()
obj.some_attribute = "value"

# 测试不同命名风格的冲突
snake_case_var = "snake"
camelCaseVar = "camel"

# 测试字符串中的标识符（不应被重命名）
message = "This is snake_case_var: {snake_case_var}"

# 测试注释中的标识符（不应被重命名）
# This is a comment about snake_case_var

if __name__ == "__main__":
    print("=== 全面作用域测试开始 ===")
    
    print(f"全局 global_var: {global_var}")
    print(f"全局 GLOBAL_CONSTANT: {GlobalConstant}")
    
    result = TestFunction()
    print(f"test_function 返回值: {result}")
    
    obj = TestClass1()
    print(f"对象 class_var: {obj.class_var}")
    print(f"类 class_var: {TestClass1.class_var}")
    obj.Method("test_param")
    
    print(f"字符串中的标识符: {message}")
    
    print("=== 全面作用域测试结束 ===")