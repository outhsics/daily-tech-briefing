"""
AI Prompt模板
"""

# 智谱AI Prompt模板
ZHIPU_PROMPTS = {
    "analyze_article": """请分析以下科技文章，并以JSON格式返回分析结果：

{article}

请返回以下格式的JSON：
{{
    "summary": "一句话总结文章核心内容（30-50字）",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "category": "文章类别（如：人工智能、移动开发、前端技术、云计算等）",
    "sentiment": "情感倾向（positive/neutral/negative）",
    "score": 0.8
}}

注意：
- summary要简洁准确
- keywords提取3-5个最重要的技术关键词
- score范围0-1，表示文章重要性和热度
""",

    "summarize_articles": """请分析以下{count}篇科技文章，生成今日科技简报：

{articles}

请以JSON格式返回：
{{
    "summary": "今日科技热点概述（100-200字），涵盖主要趋势和重要事件",
    "trending_topics": ["热点话题1", "热点话题2", "热点话题3"],
    "category": "主要分类（如：人工智能、云计算等）"
}}

要求：
- summary要简洁全面，突出重点
- trending_topics提取3-5个今日最热技术话题
- 按重要性排序
""",

    "categorize_article": """请将以下文章分类到一个最合适的技术类别：

标题：{title}

内容：{content}

可选类别：
- 人工智能
- 移动开发
- 前端技术
- 后端开发
- 云计算
- 大数据
- 区块链
- 物联网
- 安全
- 产品设计
- 创业
- 其他

只返回类别名称。
""",

    "extract_keywords": """请从以下文本中提取最重要的技术关键词：

{text}

返回5-10个关键词，用逗号分隔。
"""
}

# 通义千问 Prompt模板
QWEN_PROMPTS = {
    "analyze_article": """你是一个专业的科技资讯分析师。请分析以下文章：

{article}

请提供：
1. 一句话摘要（30-50字）
2. 3-5个关键词
3. 文章分类
4. 重要性评分（0-1）

以JSON格式返回。
""",

    "summarize_articles": """你是科技简报编辑。请基于以下文章生成今日简报：

{articles}

提供：
1. 每日概述（100-200字）
2. 3-5个热点话题
3. 主要分类

以JSON格式返回。
"""
}
