# WeHUSTER 英语四六级真题下载站 (静态归档版)

本仓库是 [WeHUSTER](https://www.wehuster.com/) 的精简与静态归档版本。为了提供一个极致干净、专注的英语四六级（CET4/6）试题与听力下载体验，本仓库已移除了所有非四六级相关的学习资料、登录注册模块、评论和底部区域。

> [!NOTE]
> **免责声明**：本项目由作者出于学习与研究目的归档并克隆，本网站并不是我本人的官方网站。原网站所有权与所有内容均归原作者所有。

---

## 🌟 项目特点

*   **极致精简**：移除了原站的微积分、线性代数、关于我们、登录注册等页面，仅保留**四级真题**与**六级真题**页面。
*   **无感跳转**：根目录 `/` 会自动重定向到 `/cet4`（四级真题），且左上角的 **WeHUSTER** Logo 直接链接至 `/cet4`，体验更流畅。
*   **完美运行的“一键下载”**：通过 `vercel.json` 里的反向代理（Rewrite）配置，直接将打包下载请求（`/api/batchdownload`）转发给原站接口处理，成功解决静态部署后“Download All”报错失败的问题。
*   **轻量化 Git 仓库**：所有的 PDF 试题和 MP3 听力音频依然指向 WeHUSTER 官方原站服务器，仓库总体积仅 ~2.6MB，加载极快，且避免了 GitHub 大文件限制。
*   **全自动增量更新**：配置了 GitHub Actions 每日自动抓取主站，如有新年份真题上传，会自动同步、提交并部署上线。

---

## 🤖 自动化更新系统

项目包含了一个轻量级且强大的自动同步与更新链条：

1.  **增量更新脚本** ([update_site.py](update_site.py))：负责对比原站的 `/cet4` 和 `/cet6` 真题列表。若有新试题发布，则只增量下载该新页面的 HTML 和预览图片，并自动清理新页面里的页眉、页脚、注水（hydration）数据等。
2.  **GitHub Actions 工作流** ([.github/workflows/update.yml](.github/workflows/update.yml))：每周日午夜（UTC 时间 0:00，北京时间周日早上 8:00）自动在云端执行更新脚本。
3.  **Vercel 自动化部署**：更新脚本若检测到变化并提交代码到 GitHub，将立刻触发 Vercel CI/CD 的自动构建与热发布。

### 🛠️ 手动触发同步更新

如果您想立即同步主站的更新，而不想等待每日的定时任务：
1. 打开您的 GitHub 仓库：[tom613951/wehuster](https://github.com/tom613951/wehuster)
2. 导航到 **Actions** 选项卡。
3. 在左侧选择 **Auto Update CET test papers** 工作流。
4. 点击 **Run workflow** 下拉菜单，然后点击绿色的 **Run workflow** 按钮启动同步。

---

## 💻 本地运行与开发

如果您想在本地测试或运行此项目：

1.  **克隆仓库**：
    ```bash
    git clone https://github.com/tom613951/wehuster.git
    cd wehuster
    ```
2.  **本地运行静态服务器**：
    您可以使用 VS Code 的 Live Server 插件，或者在终端运行 Python 简易服务器：
    ```bash
    python -m http.server 8000
    ```
    然后在浏览器中打开 `http://localhost:8000/cet4` 即可。
3.  **本地手动更新抓取**：
    ```bash
    python update_site.py
    ```
