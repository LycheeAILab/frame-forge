<div align="center">

# Frame Forge

### 把照片与灵感，变成值得收藏的一页。

六种视觉风格 · 看图选择 · 内置生图

[风格画廊](#风格画廊) · [开始使用](#开始使用) · [创作方式](#创作方式)

</div>

---

**一张照片，多种表达。** 从安静的纸刊海报，到有触感的胶带拼贴和微缩舞台。选一个风格，交给 Frame Forge，直接获得成品图片。

## 风格画廊

同一只金毛，同一个车窗，六种表达。点击图片查看预览。

<table>
  <tr>
    <td align="center" width="33%">
      <a href="assets/previews/minimal.jpg"><img src="assets/previews/minimal.jpg" height="230" alt="极简纸刊：大留白与小幅金毛摄影"></a><br>
      <strong>01 · 极简纸刊</strong><br>
      <sub>大留白 · 纸纹 · 单一亮色</sub>
    </td>
    <td align="center" width="33%">
      <a href="assets/previews/monthly.jpg"><img src="assets/previews/monthly.jpg" height="230" alt="月历明信片：金毛照片与九月水彩手记"></a><br>
      <strong>02 · 月历明信片</strong><br>
      <sub>原照片 · 水彩 · 月份手记</sub>
    </td>
    <td align="center" width="33%">
      <a href="assets/previews/abstract.jpg"><img src="assets/previews/abstract.jpg" height="230" alt="照片抽象编辑：照片与简洁的抽象图形"></a><br>
      <strong>03 · 照片抽象编辑</strong><br>
      <sub>摄影 · 抽象关系 · 干净排版</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <a href="assets/previews/gathered.jpg"><img src="assets/previews/gathered.jpg" height="230" alt="实景纸感拼贴：金毛与撕纸蓝色道路"></a><br>
      <strong>04 · 实景纸感拼贴</strong><br>
      <sub>真实摄影 · 撕纸边缘 · 结构性色彩</sub>
    </td>
    <td align="center">
      <a href="assets/previews/masking-tape.jpg"><img src="assets/previews/masking-tape.jpg" height="230" alt="纸胶带拼贴：金毛照片与胶带重构"></a><br>
      <strong>05 · 纸胶带拼贴</strong><br>
      <sub>纸胶带 · 柔和配色 · 手工触感</sub>
    </td>
    <td align="center">
      <a href="assets/previews/miniature-diptych.jpg"><img src="assets/previews/miniature-diptych.jpg" height="230" alt="手工微缩双联：金毛照片与毛毡微缩舞台"></a><br>
      <strong>06 · 手工微缩双联</strong><br>
      <sub>黏土毛毡 · 微缩舞台 · 上下双联</sub>
    </td>
  </tr>
</table>

以上为 Frame Forge 使用内置生图工具制作的风格预览。画廊图片经过缩小压缩，适合浏览；实际作品单独生成。

## 开始使用

**① 安装** — 把这句话发给 Codex：

```text
请安装 https://github.com/LycheeAILab/frame-forge 的根目录 Skill。
```

**② 选风格** — 上传照片，在新任务中说：

```text
用 $frame-forge 展示风格示例图，我选好后再生成。
```

**③ 得到作品** — 回复编号，或直接指定：

```text
用 $frame-forge 把这张照片做成第五种「纸胶带拼贴」。
```

<details>
<summary>手动安装 · macOS / Linux / Windows</summary>

macOS / Linux：

```bash
git clone https://github.com/LycheeAILab/frame-forge.git ~/.codex/skills/frame-forge
```

Windows PowerShell：

```powershell
git clone https://github.com/LycheeAILab/frame-forge.git "$env:USERPROFILE\.codex\skills\frame-forge"
```

设置了自定义 `CODEX_HOME` 时，安装到其 `skills/frame-forge` 目录。安装后在新任务中使用。

</details>

## 创作方式

| 你的想法 | 可以这样说 |
| :--- | :--- |
| 从一句话开始 | 做一张关于雨天旧书店的极简纸刊海报。 |
| 留住这个月 | 把照片做成九月明信片，署名 Lychee，其余页脚留空。 |
| 多张照片分别创作 | 每张照片单独做成纸胶带拼贴，不要合并。 |
| 把场景变成小舞台 | 用第六种，把照片中的场景做成手工微缩双联。 |

极简纸刊和手工微缩双联支持文字场景；其他风格使用源照片。纸胶带拼贴逐张输出独立的 3:4 作品。手工微缩双联采用上下等高结构，下半幅保留大面积留白。

<details>
<summary>生成与输出说明</summary>

- 使用当前会话的内置生图工具，无需在本 skill 中配置 API key。
- 提示词在内部使用，用户收到图片与简短说明。
- 选风格直接展示固定预览，不额外生成选择图。
- 内置工具不可用时说明暂时无法生成，不用提示词代替图片。
- 六种风格已完成单张示例生成与视觉检查，不承诺照片像素级一致。
- 打印规格以实际生成文件的像素和所需印刷尺寸为准。

</details>

---

<p align="center"><sub>Frame Forge · LycheeAILab</sub></p>
