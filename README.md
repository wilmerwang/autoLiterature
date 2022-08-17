# autoLiterature
**autoLiterature**是一个基于Python的自动文献管理命令行工具。Inspired by [Mu Li](https://www.bilibili.com/video/BV1nA41157y4).   

**重要：**  
- [autoLiter_web](https://github.com/WilmerWang/autoLiter_web)是一个类似的web软件。

**识别规则：**
- 自动识别 `-{xxx}`。
- 当笔记文件中包含`- {paper_id}`时候，仅会下载该文献的信息，**不下载PDF**。
- 当笔记文件中包含`- {{paper_id}}`时候，会下载该文献的信息，以及PDF。

注意：`paper_id`支持已发表文章的`doi`,预发布文章的`arvix_id`, `biorvix_id`, `medrvix_id`。

## 安装
```
pip3 install autoliter
# 或者
pip install autoliter
```

### 软件参数
```bash
autoLiterature

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
```
# 假设你要保存的pdf文件夹地址是 output = /home/cat/pdfs/
# 假设你要更新的笔记文件夹地址是 input = /home/cat/notes/
autoliter -i input -o output             # 更新input文件夹下所有md文件
autoliter -i input/example.md -o output  # 仅更新input/example.md文件

# -d 是个可选项，当 -i 是文件夹路径时候，使用-d会删除PDF文件夹下和笔记无关的pdf文件
autoliter -i input -o output -d

# -m 是个可选项，表示要迁移的PDF文件夹路径，当-m存在时，会重新链接笔记和pdf文件下的文件
autoliter -i input -m
autoliter -i input -o output -m
autoliter -i input -o output -d -m
```
## License
MIT