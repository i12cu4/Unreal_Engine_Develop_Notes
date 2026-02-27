环境配置请先看,同路径文件Construct The Android
本文[默认已经配置好Android环境]配置的Android打包以及Android调试

前置条件:
下载内容:
PC:
ADB
Mobile:
Shizuku
外设情况:
手机Usb连接PC选择传输



<details>
<summary>PC</summary>
[ADB](https://pan.baidu.com/s/1WHWjNlvXsliE9Hp9a7jB0Q?pwd=gfnd)
Win+R -> sysdm.cpl -> 高级 -> 环境变量 -> Path -> 将ADB路径存入
Win+R -> cmd -> 输入 adb version
显示版本即配置成功
<pre><code>
</code></pre>
</details>

<details>
<summary>Mobile</summary>
<pre><code>
[ShiZuku](https://www.coolapk.com/apk/moe.shizuku.privileged.api)
开启手机开发者模式 -> 设置 -> 关于手机/平板电脑 -> 找到版本号，然后连点7下，出现提示后说明成功
打开允许调试 -> 设置->系统和更新 -> 开发人员选项 -> "USB调试" 和 "'仅充电'模式下允许ADB调试"
打开Shizuku -> 查看指令 -> 复制指令
</code></pre>
</details>

将复制的指令在PC端 cmd 中输入即可激活(此时手机ShiZuku会显示已激活)

以上内容摘自https://blog.csdn.net/weixin_51094633/article/details/124658828

UE 打包Andriod 成功后
Andriod-[打包方式]文件夹下的内容:
Install_[ProjectName]-arm64.bat -> 安装usb连接的手机中的ue项目(双击打开就可以)
[ProjectName]-arm64.apk -> 这是apk包(迁移到手机上,手机打开也可以,不过没上面的方便)
Uninstall_[ProjectName]-arm64.bat -> 卸载usb连接的手机中的ue项目(双击打开就可以)
注:建议以Install_[ProjectName]-arm64的方式安装,apk有时候会有"解析错误"的未知问题

当然,你开发中肯定不是经常做"打包"这样的蠢事,
你有时候还是需要"调试"的

打包平台左边有三个点,即"修改游戏模式和游戏设置" -> 移动设备预览ES3.1(PIE) 这个是在PC上模拟Android 启动项目
用着不舒服就换个牌子,贴身的东西不要贪便宜,目前只能这样了