#include <iostream>
void func(void *ptr) 
{
    std::cout << "func ptr" << std::endl;
}
void func(int i) 
{
    std::cout << "func i" << std::endl;
}
int main() {
    //func(NULL); 编译失败，会产生二义性
    func(nullptr); // 输出func ptr
    return 0;
}