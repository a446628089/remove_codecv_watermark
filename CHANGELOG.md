# Changelog

本项目所有重要变更记录于此。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [Unreleased]

## [0.2.0] - 2026-08-19

### Added

- CLI 新增 `--backup` 参数：处理前自动将原 PDF 备份到 `源文件/` 目录，干净文件覆盖原路径（与右键菜单行为一致）
- 批量模式（目录输入）支持 `--backup`

### Changed

- 提取 GUI 右键菜单的备份逻辑为公共函数 `backup_original()`，消除重复代码

## [0.1.0] - 2026-08-19

### Added

- 支持目录批量去水印：传入文件夹一次性处理其中所有 PDF
- 新增 `--recursive` 参数：递归扫描子目录中的 PDF
- 新增 `--output-dir` 参数：将去水印结果输出到指定目录

### Fixed

- 修复 GUI 右键菜单模式误判目录参数的 bug（目录不再被当成右键菜单文件）

## [0.0.1] - 2026-07-18

### Added

- 核心功能：移除 CodeCV 导出 PDF 的 `/Pattern` 平铺水印
- 右键菜单模式（Windows），打包为独立 exe
- 命令行模式，支持指定输入/输出路径
