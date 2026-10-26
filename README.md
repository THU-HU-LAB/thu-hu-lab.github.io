# THU-HU-LAB Website

网站地址：**[thu-hu-lab.github.io](https://thu-hu-lab.github.io)**

基于 [Greene Lab Website Template](https://github.com/greenelab/lab-website-template) v1.4.0（`cca827d`）。保留上游 BSD-3-Clause 许可证与模板署名。

## 当前状态

本地成员资料与论文库已逐步替换为课题组内容，其他栏目仍可能包含模板示例。2026-10-18 论文库导入、核验范围与待核清单见 [_cite/reports/2026-10-18/README.md](_cite/reports/2026-10-18/README.md)。本地修改不代表已经推送发布。

## 日常维护

在 GitHub 上编辑以下文件并提交到 `main`，网站会自动构建并发布：

| 内容 | 文件或目录 |
| --- | --- |
| 名称、介绍、社交链接 | `_config.yaml` |
| 首页 | `index.md` |
| 成员及个人介绍 | `_members/` |
| 按成员 ORCID 同步论文 | `_members/*.md` 的 `links.orcid` |
| 论文信息及 DOI | `_data/sources-*.yaml`；胡楚雄论文为 `_data/sources-huchuxiong.yaml` |
| 项目 | `_data/projects.yaml` |
| 新闻动态 | `_posts/` |
| 联系方式 | `contact/index.md` |
| 图片 | `images/` |

部署使用 `main` 中的源文件构建，生成的网页发布到 `gh-pages` 分支。请不要直接编辑 `gh-pages`。

在仓库 **Actions → on-push** 查看构建状态。引用信息会随 `main` 更新，定期引用刷新暂未启用。

## 配置成员 ORCID

在成员 Markdown 开头的 YAML 中填写 `links.orcid`；这一个字段用于论文同步和个人页论文关联，页面不显示 ORCID 按钮。例如（请替换为该成员的真实号码）：

```yaml
links:
  orcid: "0000-0000-0000-000X"
  email: member@example.com
```

号码只填写带连字符的 ORCID iD，不要填写 `https://orcid.org/` 前缀。
没有 ORCID 时留空或删除这一项，该成员会跳过同步。格式错误时，更新日志会报告对应成员文件。
`_data/orcid.yaml` 不再作为同步来源；原模板的示例 ORCID 已移除。

同步脚本读取 ORCID 中的公开成果，并与 `_data/sources*.yaml` 中的手动记录合并；相同文献标识符的记录会合并，手动记录优先。不要直接修改自动生成的 `_data/citations.yaml`。

本次核实的完整元数据保存在 `_data/sources-huchuxiong.yaml`，带有核验日期、来源和成员 ORCID；这类记录预览时不会重复请求 Manubot。保存的核验结果是快照，需要重新核查时参照上面的报告。已下载 PDF 位于本地 `_downloads/papers/`，不随网站上传。

填写 ORCID 并不等于该账号已收录论文。如果同步完成后仍为 0 篇，请检查 ORCID 的 Works（成果）是否已有记录且设置为公开；也可手动录入并关联论文，见下文。

成员个人页按 `links.orcid` 精确列出关联论文，不再使用中英文姓名搜索。
同一篇论文出现在多位成员的 ORCID 中时，会合并成一条记录并保留全部 `orcids`，因此会同时出现在这些成员的个人页。
个人页的 Research 链接使用 `?orcid=...` 筛选；可以继续输入关键词缩小结果，或点击清除按钮查看全部文献。
未配置 ORCID 的成员不会按姓名猜测归属；如果仅手动录入一篇论文，可在 `_data/sources.yaml` 对应记录添加 `orcids: ["该成员的真实 ORCID"]` 建立关联。

本地 Docker 预览会在成员文件修改后重新运行文献脚本；ORCID 请求有 24 小时缓存，远端记录刚修改时可能不会立即刷新。升级本次监听脚本后，先停止旧预览，再运行 `bash .docker/run.sh` 一次；随后日常修改成员资料无需重建镜像。
推送到 `main` 后，现有 Actions 会同步论文并发布网站。这里没有启用额外的定时任务。

模板文档：[Lab Website Template Documentation](https://greene-lab.gitbook.io/lab-website-template-docs)。

## 中英文切换

英文版保留原网址，中文版位于 `/zh/`。导航栏的“中文 | English”切换到当前页面的对应语言，并保留搜索、成员 ORCID 筛选和章节位置。浏览器会记住语言选择，下次从首页访问时使用该语言；直接访问具体页面仍使用链接指定的语言。

| 内容 | 英文 | 中文 |
| --- | --- | --- |
| 首页及栏目 | `index.md`、`team/`、`research/` 等 | `zh/index.md`、`zh/team/`、`zh/research/` 等 |
| 成员资料 | `_members/*.md` 的现有字段和正文 | 同一文件的 `name_zh`、`description_zh`、`affiliation_zh`、`content_zh` |
| 研究方向卡片 | `_data/projects.yaml` 的现有字段 | 同一条目的 `title_zh`、`subtitle_zh`、`description_zh` |
| 新闻文章 | `_posts/*.md` 的标题和正文 | 同一文件的 `title_zh`、`content_zh` |
| 搜索、按钮等公共文案 | `_data/i18n.yaml` 的 `en` | 同一文件的 `zh` |

成员中文简介写在 YAML 开头的 `content_zh: |` 下，每行缩进两个空格。例如：

```yaml
name: Example Member
name_zh: 示例成员
description: Ph.D. Student
description_zh: 博士生
affiliation_zh: 清华大学机械工程系
content_zh: |
  这里填写中文个人介绍。

  ## 研究方向 {#research-interests}

  - 机器人运动规划
```

请保留原来的照片、`links.orcid`、邮箱和英文正文。中文成员页由 `_plugins/i18n.rb` 自动生成，不要在 `zh/members/` 复制成员文件。成员顺序统一维护在 `_includes/team-members.html`，中英文同时生效。未填写 `content_zh` 的成员或文章会显示英文原文并提示尚无中文译文。模板的技术演示页也使用此回退方式。

两种语言共用一份论文库，论文标题、作者和出版信息保留原文。中文标签仅翻译显示文字，筛选仍使用稳定的英文标签标识。修改 Markdown 和翻译文本后可以热更新；修改 Ruby 插件或 `_config.yaml` 后需要重启预览进程。

验证：先构建网站，再运行 `python _cite/tests/test_i18n.py --site-dir _site`、`node _cite/tests/test_search.cjs` 和 `node _cite/tests/test_language.cjs`。
