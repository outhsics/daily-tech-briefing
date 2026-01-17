# 贡献指南

感谢你考虑为每日科技简报生成系统做出贡献！

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/outhsics/daily-tech-briefing/issues) 中搜索现有问题
2. 如果没有找到，创建新的 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）

### 提出新功能

1. 先在 [Issues](https://github.com/outhsics/daily-tech-briefing/issues) 中讨论
2. 说明功能的使用场景和价值
3. 等待维护者反馈

### 提交代码

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 添加必要的注释和文档字符串
- 确保代码通过测试
- 更新相关文档

### 添加新数据源

1. 在 `app/scrapers/` 下创建新的爬虫文件
2. 继承 `BaseScraper` 类
3. 实现 `fetch()` 方法
4. 在 `app/scrapers/__init__.py` 中注册

示例：
```python
from app.scrapers.base import BaseScraper
from app.models.article import ScrapedArticle

class MyScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.name = "mysource"
        self.base_url = "https://example.com"

    async def fetch(self, limit: int = 10) -> List[ScrapedArticle]:
        # 实现抓取逻辑
        pass
```

### 添加新 AI 服务

1. 在 `app/ai/` 下创建新的 AI 服务文件
2. 继承 `AIServiceBase` 类
3. 实现所有抽象方法
4. 在 `app/ai/__init__.py` 中注册
5. 在 `app/config.py` 中添加配置

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/outhsics/daily-tech-briefing.git
cd daily-tech-briefing

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发工具
pip install flake8 black pytest

# 运行测试
pytest tests/

# 代码格式化
black app/
```

## 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `perf:` 性能优化
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat(scraper): 添加少数派数据源
fix(ai): 修复 OpenRouter API 调用超时问题
docs(readme): 更新安装说明
```

## 行为准则

- 尊重所有贡献者
- 欢迎不同观点的建设性讨论
- 关注对社区最有利的事情

有任何问题随时在 Issues 中提问！
