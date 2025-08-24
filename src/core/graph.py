from langgraph.graph import StateGraph, END
from src.core import nodes
from src.core.state import AgentState
from src.core.utils.utils import TODO_CATEGORIES, USER_INFO
import asyncio

class Graph:
    def __init__(self):
        workflow = StateGraph(AgentState)
        # 노드 추가
        workflow.add_node("initNode", nodes.initNode)
        workflow.add_node("managerNode", nodes.managerNode)
        workflow.add_node("gujicNode", nodes.gujicNode)
        workflow.add_node("gujicNode_sub1", nodes.gujicNode_sub1)
        workflow.add_node("jasosuMainNode", nodes.jasosuMainNode)
        workflow.add_node("elseNode", nodes.elseNode)

        workflow.add_node("outputNode", nodes.outputNode)

    
        # 그래프 연결
        workflow.set_entry_point("initNode")  
        workflow.add_edge("initNode", "managerNode")

        # 매니저 -> 역할 배분
        workflow.add_conditional_edges("managerNode", 
                                       self.select_Node,
                                       {
                                           "elseNode": "elseNode",
                                            "gujicNode": "gujicNode",
                                            "jasosuMainNode": "jasosuMainNode",
                                            "outputNode" : "outputNode", 
                                       })

        # # 역할완료 -> 매니저
        workflow.add_edge("elseNode", "managerNode")

        workflow.add_conditional_edges("gujicNode", 
                                       self.is_gujicinfo_enough,
                                       {
                                           "gujicNode_sub1": "gujicNode_sub1",
                                            "managerNode": "managerNode",
                                       })
        
        workflow.add_edge("gujicNode_sub1", "managerNode")

        workflow.add_edge("jasosuMainNode", "managerNode")
        workflow.add_edge("outputNode", END)
        self.app = workflow.compile()

    async def select_Node(self, state : AgentState):
        priority_list = state.get('priority_list')
        if not priority_list:
             return "outputNode"
        if priority_list[0][0]==TODO_CATEGORIES[0]:
                return "gujicNode"
        if priority_list[0][0]==TODO_CATEGORIES[1]:
                return "jasosuMainNode"
        return "elseNode"
    
    async def is_gujicinfo_enough(self, state : AgentState):
         priority_list = state.get('gujic_info_enough', False)
         if priority_list:
              return 'gujicNode_sub1'
         return 'managerNode'
         
        
    
    async def run(self, initial_state: dict):
        # async for event in self.app.astream(initial_state):
        #     # 스트리밍 결과 처리 (예시)
        #     for key, value in event.items():
        #         print(f"Node: {key}")
        #         print("---")
        #         print(value)
        #         print("---")
        return await self.app.ainvoke(initial_state)
