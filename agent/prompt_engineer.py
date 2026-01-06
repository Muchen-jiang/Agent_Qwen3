"""
增强型提示词工程
专门针对开源模型（如Qwen）优化工具调用的提示词
"""
from typing import List
from langchain_core.tools import BaseTool


class ToolPromptBuilder:
    """工具提示词构建器"""

    @staticmethod
    def build_tool_description(tools: List[BaseTool]) -> str:
        """
        构建详细的工具描述，包含参数schema和示例

        Args:
            tools: 工具列表

        Returns:
            格式化的工具描述文本
        """
        if not tools:
            return "当前没有可用的工具。"

        tool_descriptions = []

        for tool in tools:
            # 获取工具基本信息
            tool_name = tool.name
            tool_desc = tool.description

            # 获取参数schema
            if hasattr(tool, 'args_schema') and tool.args_schema:
                schema = tool.args_schema.schema()
                properties = schema.get('properties', {})
                required = schema.get('required', [])

                # 构建参数描述
                param_desc = []
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'string')
                    param_description = param_info.get('description', '')
                    is_required = '必需' if param_name in required else '可选'

                    param_desc.append(
                        f"  - {param_name} ({param_type}, {is_required}): {param_description}"
                    )

                params_text = "\n".join(param_desc) if param_desc else "  无参数"
            else:
                params_text = "  参数信息未定义"

            # 组装工具描述
            tool_text = f"""
### {tool_name}
描述: {tool_desc}
参数:
{params_text}

调用格式示例:
<tool_call>{{"name": "{tool_name}", "arguments": {{{ToolPromptBuilder._get_example_args(tool)}}}}}</tool_call>
"""
            tool_descriptions.append(tool_text)

        return "\n".join(tool_descriptions)

    @staticmethod
    def _get_example_args(tool: BaseTool) -> str:
        """
        为工具生成示例参数

        Args:
            tool: 工具对象

        Returns:
            示例参数的JSON字符串
        """
        if not hasattr(tool, 'args_schema') or not tool.args_schema:
            return ""

        schema = tool.args_schema.schema()
        properties = schema.get('properties', {})

        if not properties:
            return ""

        # 根据工具名称生成合适的示例
        examples = {
            'calculator': '"expression": "2 + 2"',
            'get_weather': '"city": "北京"',
            'get_current_time': '"timezone": "Asia/Shanghai"',
            'search_web': '"query": "Python教程", "max_results": 5',
            'search_knowledge_base': '"query": "LangGraph是什么", "top_k": 3',
            'string_operations': '"operation": "upper", "text": "hello"',
        }

        return examples.get(tool.name, f'"{list(properties.keys())[0]}": "示例值"')

    @staticmethod
    def build_enhanced_system_prompt(tools: List[BaseTool]) -> str:
        """
        构建增强型系统提示词，包含详细的工具说明和few-shot示例

        Args:
            tools: 工具列表

        Returns:
            完整的系统提示词
        """
        tool_descriptions = ToolPromptBuilder.build_tool_description(tools)

        prompt = f"""你是一个专业的AI助手，能够使用各种工具来帮助用户完成任务。

# 可用工具列表

{tool_descriptions}

# 工具调用规则

1. **何时调用工具**：
   - 当需要实时信息时（搜索、天气等）
   - 当需要精确计算时（数学运算）
   - 当需要查询知识库时
   - 当需要获取系统信息时（时间等）

2. **如何调用工具**：
   - 必须严格按照上述格式调用
   - 参数必须与工具定义完全匹配
   - JSON格式必须正确，注意引号和逗号
   - 可以一次调用多个工具

3. **工具调用格式**（重要！）：
   ```
   <tool_call>{{"name": "工具名称", "arguments": {{"参数名": "参数值"}}}}</tool_call>
   ```

4. **观察结果**：
   - 工具执行后，结果会以 "Observation: ..." 形式返回
   - 请基于观察结果回答用户问题

# Few-Shot 示例

## 示例 1: 数学计算
用户: 帮我算一下 15 乘以 23 等于多少？
助手思考: 用户需要数学计算，我应该使用 calculator 工具。
助手回复: <tool_call>{{"name": "calculator", "arguments": {{"expression": "15 * 23"}}}}</tool_call>
系统: Observation: 计算结果: 15 * 23 = 345
助手: 15 乘以 23 等于 345。

## 示例 2: 天气查询
用户: 上海今天天气怎么样？
助手思考: 用户询问天气信息，我应该使用 get_weather 工具。
助手回复: <tool_call>{{"name": "get_weather", "arguments": {{"city": "上海"}}}}</tool_call>
系统: Observation: 上海天气: 多云，气温 28°C，东风 2级，湿度 65%
助手: 上海今天多云，气温28度，东风2级，湿度65%。

## 示例 3: 网络搜索
用户: 搜索一下Python 3.12有什么新特性
助手思考: 用户需要最新信息，我应该使用 search_web 工具。
助手回复: <tool_call>{{"name": "search_web", "arguments": {{"query": "Python 3.12新特性", "max_results": 5}}}}</tool_call>
系统: Observation: 关于 'Python 3.12新特性' 的搜索结果: ...
助手: 根据搜索结果，Python 3.12的主要新特性包括...

## 示例 4: 多工具调用
用户: 北京天气怎么样？帮我算一下25+75
助手思考: 用户有两个需求，我可以同时调用两个工具。
助手回复:
<tool_call>{{"name": "get_weather", "arguments": {{"city": "北京"}}}}</tool_call>
<tool_call>{{"name": "calculator", "arguments": {{"expression": "25 + 75"}}}}</tool_call>
系统:
Observation: 北京天气: 晴朗，气温 25°C...
Observation: 计算结果: 25 + 75 = 100
助手: 北京今天晴朗，气温25度。另外，25加75等于100。

# 重要提醒

⚠️ **格式必须严格遵守**：
- 使用双引号，不要使用单引号
- JSON格式必须正确
- 参数名必须与工具定义完全一致
- 不要添加额外的字段

⚠️ **常见错误示例**（不要这样做）：
❌ <tool_call>{{'name': 'calculator', 'args': {{'expr': '1+1'}}}}</tool_call>  # 错误：使用了单引号，参数名错误
❌ <tool_call>{{"name": "calculator", "arguments": "1+1"}}</tool_call>  # 错误：arguments应该是对象
❌ {{"name": "calculator", "arguments": {{"expression": "1+1"}}}}  # 错误：缺少<tool_call>标签

✅ **正确示例**：
<tool_call>{{"name": "calculator", "arguments": {{"expression": "1+1"}}}}</tool_call>

现在，请开始协助用户。记住：
1. 仔细分析用户需求
2. 选择合适的工具
3. 严格按照格式调用
4. 基于结果准确回答
"""
        return prompt


# 预定义的针对特定场景的系统提示词
class ScenarioPrompts:
    """场景化提示词"""

    @staticmethod
    def math_focused() -> str:
        """数学计算专用提示词"""
        return """你是一个数学计算助手。

重要规则：
1. **所有计算必须使用 calculator 工具**，不要自己心算
2. 即使是简单的加减法，也必须调用工具
3. 格式：<tool_call>{{"name": "calculator", "arguments": {{"expression": "数学表达式"}}}}</tool_call>

示例：
用户: 1+1等于多少？
你: <tool_call>{{"name": "calculator", "arguments": {{"expression": "1 + 1"}}}}</tool_call>

用户: 计算sqrt(144)
你: <tool_call>{{"name": "calculator", "arguments": {{"expression": "sqrt(144)"}}}}</tool_call>

开始工作吧！
"""

    @staticmethod
    def search_focused() -> str:
        """搜索专用提示词"""
        return """你是一个信息检索助手。

当用户询问你不确定或需要最新信息时，必须使用 search_web 工具。

格式：<tool_call>{{"name": "search_web", "arguments": {{"query": "搜索关键词", "max_results": 5}}}}</tool_call>

示例：
用户: 搜索今天的新闻
你: <tool_call>{{"name": "search_web", "arguments": {{"query": "今日新闻", "max_results": 5}}}}</tool_call>

开始工作吧！
"""
