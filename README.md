# THU-HU-LAB Website

网站地址：**[thu-hu-lab.github.io](https://thu-hu-lab.github.io)**

基于 [Greene Lab Website Template](https://github.com/greenelab/lab-website-template) v1.4.0（`cca827d`）。保留上游 BSD-3-Clause 许可证与模板署名。

## 当前状态

当前为模板预览，成员、论文、项目、图片与联系方式均为示例，不代表课题组真实资料。正式内容确认后再替换。

## 日常维护

在 GitHub 上编辑以下文件并提交到 `main`，网站会自动构建并发布：

| 内容 | 文件或目录 |
| --- | --- |
| 名称、介绍、社交链接 | `_config.yaml` |
| 首页 | `index.md` |
| 成员及个人介绍 | `_members/` |
| 论文信息及 DOI | `_data/sources.yaml` |
| 项目 | `_data/projects.yaml` |
| 新闻动态 | `_posts/` |
| 联系方式 | `contact/index.md` |
| 图片 | `images/` |

部署使用 `main` 中的源文件构建，生成的网页发布到 `gh-pages` 分支。请不要直接编辑 `gh-pages`。

在仓库 **Actions → on-push** 查看构建状态。引用信息会随 `main` 更新，定期引用刷新暂未启用。

模板文档：[Lab Website Template Documentation](https://greene-lab.gitbook.io/lab-website-template-docs)。
