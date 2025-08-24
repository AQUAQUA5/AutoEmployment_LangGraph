from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.core.utils.utils import TODO_CATEGORIES, USER_INFO, USER_INFO_MAP, ROLE_MAP
import asyncio

from src.core.state import AgentState
from src.core.utils import prompts, parsers, utils
from src.scraper import jobkorea

# llm_base = ChatOpenAI(model="gpt-5", temperature=0)
# llm_think = ChatOpenAI(model="gpt-5", temperature=0)
llm_nano = ChatOpenAI(model="gpt-5-nano", temperature=0)

# 요구사항 추출
parser_request = PydanticOutputParser(pydantic_object=parsers.GetRequests)
prompt_request = ChatPromptTemplate.from_template(
    template=prompts.pt_requests,
    partial_variables={"format_instructions": parser_request.get_format_instructions()},
)
chain_requests = prompt_request | llm_nano | parser_request

# 정보 추출
parser_info = PydanticOutputParser(pydantic_object=parsers.GetInfo)
prompt_info = ChatPromptTemplate.from_template(
    template=prompts.pt_info,
    partial_variables={"format_instructions": parser_info.get_format_instructions()},
)
chain_info = prompt_info | llm_nano | parser_info

# 희망사항 추출
parser_prefer = PydanticOutputParser(pydantic_object=parsers.GetPrefer)
prompt_prefer = ChatPromptTemplate.from_template(
    template=prompts.pt_prefer,
    partial_variables={"format_instructions": parser_prefer.get_format_instructions()},
)
chain_prefer = prompt_prefer | llm_nano | parser_prefer

# 상세직무 추출
parser_detail = PydanticOutputParser(pydantic_object=parsers.GetDetail)
prompt_detail = ChatPromptTemplate.from_template(
    template=prompts.pt_detail,
    partial_variables={"format_instructions": parser_detail.get_format_instructions()},
)
chain_detail = prompt_detail | llm_nano | parser_detail

# 적절한 공고 선택
parser_pick_jobs = PydanticOutputParser(pydantic_object=parsers.PickJobs)
prompt_pick_jobs = ChatPromptTemplate.from_template(
    template=prompts.pt_pick_jobs,
    partial_variables={"format_instructions": parser_pick_jobs.get_format_instructions()},
)
chain_pick_jobs = prompt_pick_jobs | llm_nano | parser_pick_jobs

# 기타 --------------------------------------
prompt_else_1 = ChatPromptTemplate.from_template(
    template=prompts.pt_else_1,
)
chain_else_1 = prompt_else_1 | llm_nano 


#--최종 출력 -----------------------------------------------------------------------------
prompt_output = ChatPromptTemplate.from_template(
    template=prompts.pt_output,
)
chain_output = prompt_output | llm_nano 


# 할일정리, 정보 추출
async def initNode(state: AgentState):
    # 사전작업
    tmp_input = state.get('tmp_input')
    context_current = state.get('context_current')
    #정보 추출
    tasks = [
        chain_requests.ainvoke({"input1": tmp_input}), 
        chain_info.ainvoke({"input1": tmp_input}),
        chain_prefer.ainvoke({"input1": tmp_input}),
    ]
    results = await asyncio.gather(*tasks)
    todo_list, info, prefer, detail = results

    # 포멧 수정
    todo_list = [(i.task.value, i.message)for i in todo_list.requests]
    info = {key: utils.convert_enum_to_string(value) for key, value in info.model_dump().items()}
    prefer = {key: utils.convert_enum_to_string(value) for key, value in prefer.model_dump().items()}

    # 상세직무는 몇가지 이유로 따로
    if 'pre_role' in prefer:
        if prefer['prefer']:
            role_details = prefer['prefer']
            detail = chain_detail.ainvoke({'input1':tmp_input, 'role_details':role_details})

    # 우선순위 리스트
    priority_list = todo_list.copy()
    for i in range(len(priority_list)):
        if priority_list[i][0] == '구직활동 돕기':
            priority_list.insert(0, priority_list.pop(i))

    priority_list.insert(0, ('초기화', '초기화'))

    final_dict = {'todo_list':todo_list, 'priority_list' : priority_list, **info, **prefer}
    final_dict = {key: value for key, value in final_dict.items() if value}
    return final_dict

async def managerNode(state: AgentState):
    print(state)
    priority_list = state.get('priority_list', []).copy()
    priority_list.pop(0)
    return {
        'priority_list' : priority_list,
    }

async def gujicNode(state: AgentState):
    gujic_result = state.get('gujic_result', []).copy()
    empty_info = []
    for key in USER_INFO:
        if not state.get(key):
            empty_info.append(key)

    empty_info_tr = [USER_INFO_MAP[i] for i in empty_info]
    gujic_result.append('구직과 자소서 작성에 필요한 다음 정보가 없습니다. ' + str(empty_info_tr))

    if ("pre_role" in empty_info):
        return {
            "gujic_info_enough" : False,
            "gujic_result" : gujic_result,
            "empty_info" : empty_info,
        }

    if ('pre_role_detail' in empty_info):
        detail_list = await jobkorea.get_role_sub_categories(state.get('pre_role'))
        gujic_result.append('특히 상세직무에 대한 정보가 필요합니다. '+ str(detail_list)+' 중에서 희망하는 직무가 있나요?')
        return {
            "gujic_info_enough" : False,
            "gujic_result" : gujic_result,
            "empty_info" : empty_info,
        }
    
    if (len(empty_info) < len(USER_INFO) * 0.8):
        return {
            "gujic_info_enough" : False,
            "gujic_result" : gujic_result,
            "empty_info" : empty_info,
        }
    
    return {
            "gujic_info_enough" : True,
            "gujic_result" : gujic_result,
            "empty_info" : empty_info,
        }



async def gujicNode_sub1(state: AgentState):
    gujic_result = state.get('gujic_result', []).copy()
    pre_role_detail = state.get('pre_role_detail', [])
    pre_location = state.get('pre_location', [])
    career = state.get('career', [])
    education = state.get('education', [])
    pre_company_type = state.get('pre_company_type', [])
    pre_employee_type = state.get('pre_employee_type', [])
    licenses = state.get('licenses', [])
    prefer_condition = state.get('prefer_condition', [])
    pre_benefits = state.get('pre_benefits', [])


    info1 = [('직무', ROLE_MAP[i], i) for i in pre_role_detail]
    info2 = [('근무지역', i) for i in pre_location] + \
            [('경력', i) for i in career] + \
            [('학력', i) for i in education] + \
            [('기업형태', i) for i in pre_company_type] + \
            [('고용형태', i) for i in pre_employee_type] + \
            [('자격증', i) for i in licenses] + \
            [('우대조건', i) for i in prefer_condition] + \
            [('복리후생', i) for i in pre_benefits]
    print(info1, info2)
    job_num, job_list = await jobkorea.search_job_list(info1, info2)

    if len(job_list) > 10:
        user_info = f"""
            학력:{state.get('education', '없음')},
            경력:{state.get('career', '없음')},
            전공:{state.get('major', '없음')},
            희망 연봉:{state.get('pre_salary', '없음')},
            사용자 주요 경험:{state.get('main_experience', '없음')},
            추가 희망사항 : {state.get('pre_request', '없음')},
        """
        con_context = state.get('con_context', '')
        tmp_input = state.get('tmp_input', '')
        job_list_for_ai = [str(idx)+'번 구직공고 정보 : <<<' + job_info[2] + '>>>' for idx, job_info in enumerate(job_list)]

        result = await chain_pick_jobs.ainvoke({"user_info" : user_info, 'con_context' : con_context, 'tmp_input': tmp_input, "job_list":job_list})
        result.model_dump()
        indexes = result.indexes
        reason = result.reason
        gujic_result.append(reason)
        new_job_list = [job_list[idx] for idx in indexes]
    return {
        "job_list": new_job_list,
        "gujic_result" : gujic_result,
    }



async def elseNode(state: AgentState):
    input1 = state.get('priority_list')
    input1 = input1[0]
    else_result = await chain_else_1.ainvoke({"input1" : input1})
    
    return {
        "else_result" : else_result.content
    }

async def jasosuMainNode(state: AgentState):

    return {

    }

async def outputNode(state: AgentState):
    tmp_input = state.get('tmp_input', '')
    todo_list = state.get('todo_list', '').copy()
    gujic_result = state.get('gujic_result', '').copy()
    jasosu_result = state.get('jasosu_result', '').copy()
    else_result = state.get('else_result', '').copy()
    
    output = await chain_output.ainvoke({#"tmp_input": tmp_input, 
                                         "todo_list": todo_list, 
                                         "gujic_result":gujic_result,
                                         "jasosu_result" : jasosu_result, 
                                         "else_result": else_result,
                                         })
    return {
        "con_current": [tmp_input, output],
        # "context_current": [],
        # "tmp_input": "",
        # "todo_list": [],
        # "priority_list": [],
    }