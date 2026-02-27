本文安卓打包环境:

搭建Android环境:
下载内容:
Epic-UnrealEngine 5.2.1
.Net
JDK
WDK
Visual Studio
Android Studio(SDK And NDK)


<details>
<summary>UnrealEngine 5.2.1</summary>
<pre><code>
Epic -> 库 -> 5.2.1(启动右边的箭头) -> 选项 -> 目标平台 -> Android 选择下载
</code></pre>
</details>

<details>
<summary>.Net(避免问题下载了多个组件):</summary>
<pre><code>

[.NET Core 3.1](https://dotnet.microsoft.com/zh-cn/download/dotnet/3.1)
[.NET 8.0](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
</code></pre>
</details>

<details>
<summary>JDK(避免问题下载了多个组件):</summary>
<pre><code>

[JDK : Java Development Kit 8](https://www.oracle.com/java/technologies/downloads/#java8-windows) 
[Java SE : Java Platform，Standard Edition 17.0.8](https://www.oracle.com/java/technologies/downloads/#jdk17-windows)
[Java SE : Java Platform，Standard Edition 21](https://www.oracle.com/java/technologies/downloads/#jdk21-windows)
</code></pre>
</details>

<details>
<summary>WDK:</summary>
<pre><code>

[Windows Software Development Kit 10.0.22621.1778](https://developer.microsoft.com/zh-cn/windows/downloads/windows-sdk/)
注:如果有旧版本,可以先跳过该步骤,环境运行出问题时,用geek卸载重启后再来安装它
</code></pre>
</details>

<details>
<summary>Visual Studio 2022:</summary>
<pre><code>
[VS](https://visualstudio.microsoft.com/zh-hans/vs/) 组件:
C++的桌面开发
通用Windows平台开发
使用C++的移动开发
使用C++的游戏开发
</code></pre>
</details>

<details>
<summary>Android Studio(SDK And NDK):</summary>
<pre><code>
[Android Studio 4.0 (注:ue5.2必须4.0以上,否则未知错误)](https://developer.android.google.cn/studio?hl=zh-cn)
Android SDK(安装Andriud Studio的SDK Manager)的SDK Platforms下载内容:
**Android UpsideDownCakePrivacySandbox Preview**
Android 12L("Sv2") / 10.0("Q") / 9.0("Pie") / 7.1.1("Nougat") / **5.0("Lollipop")** (注:本文试用的是5.0,另外四个版本可以暂不下载)
Android NDK(安装Andriud Studio的NDK Manager)的SDK Tools下载内容:
Android SDK Build-Tools 34 - **29.0.2** / 28.0.3 / 25.0.3 / 21.1.2(注:避免问题遂都下了,但是实际上用的是最高版本,前者是ue5.2最低要求,后者是4.27.2的最低要求)
NDK(Side by side) - **25.1.8937393** / 21.4.7075529 (注:前者是ue5.2最低要求,后者是4.27.2的最低要求,本文使用前者)
Android SDK Command-line Tools(latest) - **全选**
Cmake - **3.10.2.4988404**
**Android Emulator**
**Android SDK Platform-Tools**
注:黑体是必须下载的,其他是可选的(推荐全下,因为我出过了很多问题,目前是个人理解的最优解...)
</code></pre>
</details>

好了,以上是安装Android的前置安装内容

创建一个UE5.2.1项目,以"游戏-第一人称游戏"为例,新建时选项
蓝图
目标平台:Mobile
质量预设:Scalable(减少性能开销)
初学者内容包:不勾(减少包大小)
光线追踪:不勾(减少cpu开销)

新建完成后,打开"uproject",等待Shader编译完成后

<details>
<summary>相关设置:</summary>
<pre><code>
项目设置 - 平台 - Android - APK Packing - 平台文件配置
项目设置 - 平台 - Android - APK Packing - Minimum SDK Version (SDK版本...应该跟Android Studio 的SDK组件负载有关)
项目设置 - 平台 - Android - APK Packing - Target SDK Version (SDK版本...应该跟Android Studio 的SDK组件负载有关)
项目设置 - 平台 - Android - APK Packing - Package game data inside .apk? (打勾)
项目设置 - 平台 - Android - Google Play Services - 平台文件配置
项目设置 - 平台 - Android SDK - SDKConfig(五个内容的填写):
    C:/Users/[UserName]/AppData/Local/Android/Sdk(这是SDK路径)
    C:/Users/[UserName]/AppData/Local/Android/Sdk/ndk/25.1.8937393(这是NDK路径,ue5.2.1最低要求是该版本)
    C:/Program Files/Java/jdk1.8.0_202(这是JDK 8路径,我用的202版本)
    latest(这是使用哪个SDK打包和编译Java,'latest'表示磁盘上最新版本,'matchndk'表示匹配NDK API的版本)
    android-21(使用哪个NDK编译,'latest'表示磁盘上的最新版本,选择'android-21'或更高版本将无法在5.0之前的设备上运行,笔者手机是Huawei HarmonyOS 2.0,因为笔者生活习惯没有升级,该版本可以运行Android10.0以下的版本,遂使用该版本)
</code></pre>
</details>

经过以上步骤,就可以完成Android 打包了
