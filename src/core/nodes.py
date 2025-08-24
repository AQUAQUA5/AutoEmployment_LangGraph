from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.vectorstores import Chroma
import chromadb
from src.core.utils.utils import TODO_CATEGORIES, USER_INFO, USER_INFO_MAP, ROLE_TO_DETAIL_MAP, DETAIL_TO_ROLE_MAP
from src.core.utils.config import CHROMA_DB_PATH
import asyncio

from src.core.state import AgentState
from src.core.utils import prompts, parsers, utils
from src.scraper import jobkorea
from src.scraper import jasosu_scraper

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

# 자소서--------------------------------
# 경험 판단
parser_enoughEx = PydanticOutputParser(pydantic_object=parsers.EnoughEx)
prompt_enoughEx = ChatPromptTemplate.from_template(
    template=prompts.pt_enoughEx,
    partial_variables={"format_instructions": parser_enoughEx.get_format_instructions()},
)
chain_enoughEx = prompt_enoughEx | llm_nano | parser_enoughEx

# 문서 평가
parser_eval_doc = PydanticOutputParser(pydantic_object= parsers.Evaluation)
prompt_eval_doc = ChatPromptTemplate.from_template(
    template=prompts.pt_eval_doc,
    partial_variables={"format_instructions": parser_eval_doc.get_format_instructions()},
    )
chain_eval_doc = prompt_eval_doc | llm_nano | parser_eval_doc


# 기타 --------------------------------------
prompt_else_1 = ChatPromptTemplate.from_template(
    template=prompts.pt_else_1,
)
chain_else_1 = prompt_else_1 | llm_nano 

# 자소서 생성 ------------
prompt_gen_jasosu = ChatPromptTemplate.from_template(
    template=prompts.pt_gen_jasosu,
)
chain_gen_jasosu = prompt_gen_jasosu | llm_nano 


#--최종 출력 -----------------------------------------------------------------------------
prompt_output = ChatPromptTemplate.from_template(
    template=prompts.pt_output,
)
chain_output = prompt_output | llm_nano 

# 임베딩
embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(
    name='my_collection',
    metadata={"embedding_model": "text-embedding-3-small"}
)


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
    todo_list, info, prefer = results

    # 포멧 수정
    todo_list = [(i.task.value, i.message)for i in todo_list.requests]
    info = {key: utils.convert_enum_to_string(value) for key, value in info.model_dump().items()}
    prefer = {key: utils.convert_enum_to_string(value) for key, value in prefer.model_dump().items()}

    # 우선순위 리스트
    priority_list = todo_list.copy()
    for i in range(len(priority_list)):
        if priority_list[i][0] == '구직활동 돕기':
            priority_list.insert(0, priority_list.pop(i))

    priority_list.insert(0, ('초기화', '초기화'))

    final_dict = {'todo_list':todo_list, 'priority_list' : priority_list, **info, **prefer}

    # 상세직무는 몇가지 이유로 따로
    if 'pre_role' in prefer:
        if prefer['pre_role']:
            role_details = ROLE_TO_DETAIL_MAP[prefer['pre_role'][0]]
            detail = await chain_detail.ainvoke({'input1':tmp_input, 'role_details':role_details})
            detail = {key: utils.convert_enum_to_string(value) for key, value in detail.model_dump().items()}
            final_dict = {**final_dict, **detail}

    final_dict = {key: value for key, value in final_dict.items() if value}

    return final_dict

async def managerNode(state: AgentState):
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

    info1 = [('직무', DETAIL_TO_ROLE_MAP[i], i) for i in pre_role_detail]
    info2 = [('근무지역', i) for i in pre_location] + \
            [('경력', i) for i in career] + \
            [('학력', i) for i in education] + \
            [('기업형태', i) for i in pre_company_type] + \
            [('고용형태', i) for i in pre_employee_type] + \
            [('자격증', i) for i in licenses] + \
            [('우대조건', i) for i in prefer_condition] + \
            [('복리후생', i) for i in pre_benefits]
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
    else_result = state.get('else_result')
    result = await chain_else_1.ainvoke({"input1" : input1})
    else_result.append(result.content)
    return {
        "else_result" : else_result
    }

# 정보 충분한가 확인
async def jasosuMainNode(state: AgentState):
    input1 = state.get('main_experience', []).copy()
    result = await chain_enoughEx.ainvoke({"input1" : input1})
    result = result.model_dump()
    jasosu_info_enough = result['isEnough']
    if jasosu_info_enough:
        jasosu_search_keyword = '전공 : ' + str(state.get('major', []).copy())+ \
                                '직무: ' + str(state.get('pre_role', []).copy()) + \
                                '상세 직무: ' + str(state.get('pre_role_detail', []).copy()) 
        return {
            "jasosu_search_keyword": jasosu_search_keyword,
            "jasosu_info_enough" : jasosu_info_enough
        }
    return {
        'jasosu_result' : '자소서를 작성하기 위한 경험과 성장환경에 대한 정보가 부족합니다.',
        "jasosu_info_enough" : jasosu_info_enough,
    }

async def jasosuNode_sub1(state: AgentState):   # 검색
    jasosu_search_keyword = state.get('jasosu_search_keyword', '')
    jasosu_documents = state.get('jasosu_documents', []).copy()
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embedding_function
    )
    retrieved_docs = vectorstore.similarity_search(jasosu_search_keyword, k=5)
    jasosu_documents.extend(retrieved_docs)
    return {"jasosu_documents": retrieved_docs}

async def jasosuNode_sub2(state: AgentState):   # 평가
    jasosu_search_keyword = state["jasosu_search_keyword"]
    documents = state["documents"]
    filtered_docs = []
    for doc in documents:
        response = await chain_eval_doc.ainvoke({
            "question": jasosu_search_keyword,
            "document_content": doc.page_content,
        })
        if response['is_useful'] == 'yes':
            filtered_docs.append(doc)
    return {"filtered_documents": filtered_docs}

async def jasosuNode_sub3(state: AgentState):   # 외부 데이터 추가
    jasosu_documents = state.get('jasosu_documents', []).copy()
    if state['pre_role']:
        link_list = await jasosu_scraper.get_jasosu(state['pre_role'])
        documents_to_add = []
        for link in link_list:
            jasosu = await jasosu_scraper.get_jasosu_context(link)
            documents_to_add.append(jasosu)
            collection.add(
                documents=documents_to_add,
            )
        jasosu_documents.extend(documents_to_add)
    return {
        "jasosu_documents" :jasosu_documents
    }

async def jasosuNode_sub4(state: AgentState):   # 생성
    jasosu_filtered_documents = state.get('jasosu_filtered_documents', '').copy()
    jasosu_main = await chain_gen_jasosu.ainvoke({'input1': state['jasosu_search_keyword'],
                                                  'input2': state['jasosu_filtered_documents']
                                                  })
    jasosu_main = jasosu_main.content
    return {
        "jasosu_filtered_documents" : jasosu_filtered_documents,
        'jasosu_main' : jasosu_main
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
    output = output.content
    return {
        "con_current": [tmp_input, output],
        # "context_current": [],
        # "tmp_input": "",
        "todo_list": [],
        "priority_list": [],
    }