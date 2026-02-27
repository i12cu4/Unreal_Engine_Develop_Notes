使用cmd调用python脚本
    插件启用 -> Python Editor Script Plugin (注:python 3.9)
    项目设置 -> 插件 -> Python -> 高级 -> 开发者模式(所有用户) 打勾
    -> 打开输出日志 命令行 
        选择"cmd" 输入:
            "py [python脚本路径]" 便会调用py脚本
        选择"python" 输入:
            unreal.log("Load txext.py")
            -> 即会输出:
            LogPython: unreal.log("Load txext.py")
            LogPython: Load txext.py

使用python蓝图节点(仅在编辑器工具控件和编辑器工具蓝图可用)
    Execute Console Command节点
        输入Command -> "py [python脚本路径]" 便会调用py脚本
        unreal.py路径位置:[YourProjectFile]\Intermediate\PythonStub\unreal.py
        脚本也可以写入其中(便于import unreal)
    Execute Python Command节点
        插件启用 -> Editor Scripting Utilities(批量处理)
        创建蓝图 -> 选择 AssetActionUtility 蓝图类
        (此蓝图节点中)
        即可访问(Python)蓝图节点
        execute python command advanced 键入代码或者文件执行

蓝图库封装:
text.py代码示例:
```
import unreal
unreal.log("Load python to txext.py")
@unreal.uclass()
class PyBPFunctionLibrary(unreal.BlueprintFunctionLibrary):
    @unreal.ufunction(static=True,meta=dict(Category="Python Blueprint"))
    def PyFunction():
        unreal.SystemLibrary.print_string(None,'Python Test Function Run',text_color=[255,255,255,255])
```
项目设置 -> 插件 -> python -> 启动脚本 -> 输入test.py的路径 -> 重启项目 即显示内容

problem:
使用python制作的蓝图节点会因为重新项目而丢失蓝图节点目标
method:
项目Plugins中添加[PythonBlueprintFixer](https://github.com/Gradess2019/PythonBlueprintFixer)重新生成项目即可.

参考文章
https://zhuanlan.zhihu.com/p/395027673
https://zhuanlan.zhihu.com/p/445540668
https://zhuanlan.zhihu.com/p/256345905
https://docs.unrealengine.com/4.26/zh-CN/ProductionPipelines/ScriptingAndAutomation/Blueprints/ScriptedActions/