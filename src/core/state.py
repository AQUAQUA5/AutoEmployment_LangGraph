from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
    
class AgentState(TypedDict):
    con_current : Annotated[list, add_messages]
    context_current : Annotated[list, add_messages]
    tmp_input : str
    todo_list : list
    priority_list : list
    # 유저 정보---------------------------
    education : list
    major : list
    career : list
    licenses : list
    prefer_condition : list
    main_experience : list

    pre_salary : list
    pre_location : list
    pre_industry : list

    pre_role : list
    pre_role_detail : list

    pre_company_type : list
    pre_employee_type : list
    pre_request : list

    keywords : list
    # 구직 작업 --------------------------
    gujic_result : list
    empty_info : list   # 아직 없는 정보의 키
    job_list : list
    gujic_info_enough : bool
    # 자소서 작업 --------------
    jasosu_result : list
    jasosu_search_keyword : str
    jasosu_main : str
    jasosu_com_dict : dict
    jasosu_info_enough : str
    jasosu_documents : list
    jasosu_documents_grade : str
    jasosu_filtered_documents : list
    jasosu_no_more_data : bool

    # 기타 작업 -------------
    else_result : list

def state_init() -> dict:
    initial_state = {
        "con_current": [],
        "context_current": [],
        "tmp_input": "",
        "todo_list": [],
        "priority_list": [],

        # 유저정보-- 
        "education": [],
        "major": [],
        "career": [],
        "licenses": [],
        "prefer_condition": [],
        "main_experience": [],
        # 희망정보
        "pre_salary": [0],
        "pre_location": [],
        # 산업 직무
        "pre_industry": [],
        "pre_role": [],
        "pre_role_detail": [],
        "pre_company_type": [],
        "pre_employee_type": [],
        "pre_benefits": [],
        "pre_request": [],
        "keywords": [],

        # --구직 작업
        "gujic_result" : [],
        "gujic_info_enough" : False,
        "empty_info" : [],
        "job_list" : [],

        # 자소서 작업
        "jasosu_main": "",
        "jasosu_com_dict": {},
        "jasosu_result" : [],
        'jasosu_info_enough' : 'No', 
        "jasosu_search_keyword" : '',
        'jasosu_documents' : [],
        'jasosu_filtered_documents':[],
        'jasosu_documents_grade' : 'no',
        'jasosu_no_more_data' : False,
        # 기타 작업
        "else_result" : [],
        }
    return initial_state



