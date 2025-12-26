[官方专题]([MetaHuman | 逼真人类创建器 - 虚幻引擎 - Unreal Engine](https://www.unrealengine.com/zh-CN/metahuman))

[人物编辑](https://metahuman.unrealengine.com)

[Bridge配合使用]([Quixel Bridge - Manage 3D content and export with one click](https://quixel.com/bridge))

[使用指南]([下载MetaHuman并导出至虚幻引擎5和Maya | MetaHuman 文档 | Epic Developer Community (epicgames.com)](https://dev.epicgames.com/documentation/zh-cn/metahuman/downloading-and-exporting-metahumans))

优点:

可以轻量化编辑人物面部服装体型等方式并导入到UE工程中(非常逼真,毛发等等也很细节)

可以配合设备使用动作捕捉适配Sequencer(包括面部动画)

缺点:

不是Pawn,不能以Character访问方式使用,也没有人物应有的物理效果,需要二次开发(可以播放动画序列)

服装单一,需要导出FBX再以其他处理三维模型的软件进行二次编辑(有点繁琐)

尝试兼容UE5小白人动画,但使用状态机等蓝图类的情况下并不能能够成功(因为骨骼插槽等姜蓉问题出错,UE5.4起会因为骨骼不兼容而产生cpp静态断言的崩溃)

-> 不兼容UE4小白人 
```
使用 Bridge 请按照以下步骤作：

打开桥接器（Open Bridge） ：
启动桥接器应用程序，然后导航到 我的Metahuman（My Metahumans） 分段。
下载设置：

单击“模型”选项卡下的“下载设置”。

选择格式（Select Format） ：
选择 Metahumans： UAsset + 源资产（Source Asset）。这将允许你下载与各种版本的虚幻引擎（包括UE4）兼容的格式的超人类。

安装插件：
确保为您正在使用的相应程序下载并安装 Bridge 插件，确保正确导入文件。
通过执行这些步骤，你应该能够在虚幻引擎4中使用Bridge中的Metahuman，而不会出现兼容性问题。


Follow the steps below using Bridge:

Open Bridge:
Launch the Bridge application and navigate to the My Metahumans section.
Download Settings:

Click on Download Settings under the Models tab.

Select Format:
Choose Metahumans: UAsset + Source Asset. This will allow you to download metahumans in a format compatible with various versions of Unreal Engine, including UE4.

Install the Plugin:
Make sure to download and install the Bridge plugin for the respective program you’re using, ensuring proper import of the files.
By following these steps, you should be able to use Metahumans from Bridge in Unreal Engine 4 without compatibility issues.

```

注意:目前发现metahuman(及其相关插件)并不支持移动端打包使用(UE5.6)