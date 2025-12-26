
打包环境设置:
项目设置 -> 平台 -> Android SDK ->>>
Location of Android SDK -> C:/Users/chru/AppData/Local/Android/Sdk
Location of ANdroid NDK -> C:/Users/chru/AppData/Local/Android/Sdk/ndk/27.3.13750724
Location of JAVA -> C:/Program Files/Java/jdk-21
SDK API Level -> latest
NDK API Level -> android-26

项目启动后报错:
1.No Google Play Store Key
No OBB found and no store key to try to download.Please set one up in Android Project Settings.

由于资源比较大unreal自动生成了一个obb, obb的使用要用到google play store所以会报“No Google Play Store Key”错误

解决方法:
项目设置 -> 平台 -> Andoird -> Package game data inside .apk? -> 打勾

2.运行红字报错On mobile the SkyAtmosphere component needs a mesh with a material tagged as IsSky and using the SkyAtmosphere nodes to visualize the Atmosphere.

对场景中的 BP_Sky_Sphere 细节面板

Colors Determined By Sun Position 打勾

3.oystick摇杆和UMG button在移动端冲突的问题：按住摇杆时，UMG button按了不起作用。

UMG button的Is Focusable属性设置为false