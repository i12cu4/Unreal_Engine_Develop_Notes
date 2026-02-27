下载ocr库

```
python -m venv myenv
myenv\Scripts\activate  # 在 Windows 上激活虚拟环境
source myenv/bin/activate  # 在 Linux 或 macOS 上激活虚拟环境
pip install easyocr
```

mistake:
```
>>> import easyocr
OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized.
OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. That is dangerous, since it can degrade performance or cause incorrect results. The best thing to do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, but that may cause crashes or silently produce incorrect results. For more information, please see http://www.intel.com/software/products/support/.
```
method:
```
//代码开头添加
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
```

初始化Reader()实例的参数有：

lang_list (list)：识别语言代码，比如[‘ch_sim’,’en’]分别表示简体中文和英文。
gpu (bool, string, default = True) ：是否使能GPU，只有安装了GPU版本才有效。
model_storage_directory (string, default = None) ：模型存储位置，依次查找系统变量EASYOCR_MODULE_PATH (preferred)、MODULE_PATH (if defined)表示的路径或者~/.EasyOCR/路径。
download_enabled (bool, default = True)：如果没有对应模型文件时，自动下载模型。
user_network_directory (bool, default = None) ：用户自定义识别网络的路径，如果没有指明，则在MODULE_PATH + ‘/user_network’ (~/.EasyOCR/user_network)目录中查找。
recog_network (string, default = ‘standard’) ：替代标准模型，使用自定义的识别网络。
detector (bool, default = True) ：是否加载检测模型。
recognizer (bool, default = True) ：是否加载识别模型。