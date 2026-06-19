# CodeCV Resume Watermark Remover

一个用于移除 CodeCV 导出简历 PDF 平铺水印的小脚本。

脚本会删除 PDF 内容流中的 `/Pattern` 平铺水印绘制指令，不会把 PDF 转成图片再涂白，因此可以尽量保留原始文本、头像、排版和页面尺寸。

## 功能

- 移除 CodeCV 导出 PDF 中的浅灰色 `CodeCV简历` 平铺水印
- 保留原 PDF 页数、页面尺寸和可抽取文本
- 支持命令行指定输入、输出路径
- 如果不指定输出路径，会自动生成 `*.clean.pdf`

## 安装

需要 Python 3.10+。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

也可以直接使用已有 Python 环境安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

## 使用

指定输出文件：

```bash
python3 remove_codecv_watermark.py "带水印简历.pdf" "去水印简历.pdf"
```

不指定输出文件时，默认输出到同目录的 `.clean.pdf` 文件：

```bash
python3 remove_codecv_watermark.py "带水印简历.pdf"
```

运行成功后会看到类似输出：

```text
Removed 2 CodeCV watermark pattern fill(s).
Wrote: 带水印简历.clean.pdf
```

## 快速检查

```bash
python3 remove_codecv_watermark.py --help
```

如果能正常显示帮助信息，说明依赖安装和脚本入口正常。

## 注意事项

- 本脚本主要针对 CodeCV 当前导出的 `/Pattern` 平铺水印 PDF。
- 如果 CodeCV 后续改变导出实现，脚本可能需要调整。
- 仓库默认通过 `.gitignore` 忽略所有 `*.pdf`，避免误上传真实简历或个人信息。
- 上传 GitHub 前建议运行 `git status`，确认没有把个人 PDF 加入版本控制。
