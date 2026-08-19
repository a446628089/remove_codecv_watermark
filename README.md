# CodeCV Resume Watermark Remover

一个用于移除 CodeCV 导出简历 PDF 平铺水印的小工具。

脚本会删除 PDF 内容流中的 `/Pattern` 平铺水印绘制指令，不会把 PDF 转成图片再涂白，因此可以尽量保留原始文本、头像、排版和页面尺寸。

## 功能

- 移除 CodeCV 导出 PDF 中的浅灰色 `CodeCV简历` 平铺水印
- 保留原 PDF 页数、页面尺寸和可抽取文本
- **右键菜单模式**：右键 PDF 文件 → "Remove CodeCV Watermark" → 弹窗提示结果
- 命令行模式：支持指定输入/输出路径
- **批量模式**：传入目录，一次性处理其中所有 PDF（支持递归子目录）

## 快速开始

### 1. 打包

```bash
scripts\build.bat
```

完成后 `dist\RemoveCodecvWatermark.exe` 即打包好的独立可执行文件。

### 2. 注册右键菜单

右键 `scripts\register_context_menu.ps1` → **Run with PowerShell**

### 3. 使用

在任意 CodeCV 导出的 PDF 上右键 → **Remove CodeCV Watermark**

同目录下会生成 `原文件名.clean.pdf`。

> 卸载右键菜单：右键 `scripts\unregister_context_menu.ps1` → Run with PowerShell

## 命令行用法

```bash
python src/remove_codecv_watermark.py "带水印简历.pdf"
python src/remove_codecv_watermark.py "带水印简历.pdf" "去水印简历.pdf"
```

### 批量处理

```bash
# 处理目录下所有 PDF（原地生成 *.clean.pdf）
python src/remove_codecv_watermark.py "简历文件夹"

# 递归扫描子目录
python src/remove_codecv_watermark.py "简历文件夹" --recursive

# 批量输出到指定目录
python src/remove_codecv_watermark.py "简历文件夹" --output-dir "已去水印"

# 单文件输出到指定目录
python src/remove_codecv_watermark.py "带水印简历.pdf" --output-dir "已去水印"
```

## 项目结构

```
root/
├── src/
│   └── remove_codecv_watermark.py    # 核心去水印脚本
├── scripts/
│   ├── build.bat                     # 打包 exe
│   ├── register_context_menu.ps1     # 注册右键菜单
│   └── unregister_context_menu.ps1   # 卸载右键菜单
├── dist/                             # 构建输出（gitignore）
│   └── RemoveCodecvWatermark.exe
├── requirements.txt
├── README.md
└── .gitignore
```

## 注意事项

- 本工具主要针对 CodeCV 当前导出的 `/Pattern` 平铺水印 PDF。
- 如果 CodeCV 后续改变导出实现，脚本可能需要调整。
- 右键菜单通过 HKCU 注册，**无需管理员权限**，仅对当前用户生效。
