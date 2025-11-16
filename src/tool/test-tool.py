from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.retrievers import WikipediaRetriever

# 初始化 DuckDuckGo 搜索工具
search_tool = DuckDuckGoSearchRun()

# 初始化 Wikipedia 检索器作为本地向量数据库的替代
retriever = WikipediaRetriever()

tools = [
    Tool(
        name="Search",
        func=lambda q: search_tool.invoke(q),
        description="在互联网上搜索答案"
    ),
    Tool(
        name="Lookup",
        func=lambda q: "\n".join([doc.page_content for doc in retriever.get_relevant_documents(q)]),
        description="从本地向量数据库中检索相关文档"
    ),
    # 可扩展其他工具
]

