# autoLiterature
**autoLiterature**是一个基于Python的自动文献管理命令行工具。Inspired by [Mu Li](https://www.bilibili.com/video/BV1nA41157y4).   


**识别规则：**
- 自动识别 `- {xxx}`。
- 当笔记文件中包含`- {paper_id}`时候，会下载该文献的信息，**不下载PDF**。
- 当笔记文件中包含`- {{paper_id}}`时候，会下载该文献的信息，以及PDF。

注意：`paper_id`支持已发表文章的`doi`,预发布文章的`arvix_id`, `biorvix_id`, `medrvix_id`。

## 安装
1. pip 安装
```bash 
pip install autoliter
或者
pip3 install autoliter
```

2. 源码安装
```bash
git clone https://github.com/WilmerWang/autoLiterature.git
cd autoLiterature
python setup.py install 
```

### 软件参数
```bash
autolter

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The path to the note file or note file folder.
  -o OUTPUT, --output OUTPUT
                        Folder path to save paper pdfs and iamges. NOTE: MUST BE FOLDER
  -p PROXY, --proxy PROXY
                        The proxy. e.g. 127.0.0.1:1080
  -d, --delete          Delete unreferenced attachments in notes. Use with caution,
                        when used, -i must be a folder path including all notes
  -m MIGRATION, --migration MIGRATION
                        the pdf folder path you want to reconnect to
```

## 使用
### 基本使用
假设`input`为文献笔记(md文件)的文件夹路径，`output`为要保存PDF的文件夹路径。

```bash
# 更新input文件夹下所有md文件
autoliter -i input -o output 

# 仅更新input/example.md文件
autoliter -i input/example.md -o output  

# -d 是个可选项，当 -i 是文件夹路径时候，使用 -d 会删除PDF文件夹下和文献笔记内容无关的pdf文件
autoliter -i input -o output -d
```

### 迁移笔记和PDF文件
当要移动文献笔记或者PDF文件夹的时候，文献笔记中的PDF链接可能会变的无法使用。可以使用`-m`来重新关联PDF文件和文献笔记。

```bash
# 更新input文件夹下所有md文件
autoliter -i input -m movedPDFs/

# 仅更新input/example.md文件
autoliter -i input/example.md -m movedPDFs/  
```

更多可以本地查看[jupyter note](doc/autolter_example.ipynb)，或者在线查看[github](https://github.com/WilmerWang/autoLiterature.git) doc文件夹。

## License
MIT