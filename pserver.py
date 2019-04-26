from flask import Flask, request, jsonify
from graph.knowledgeGraph import KnowledgeGraph
from retrieved.searchManager import SearchManager
from retrieved.search_manager_v2 import SearchManagerV2, SearchResult
from custom_types import EducationalResourceType
from learningPath import LearningPathSponsor
from learningPath.utils.skill_mapper import SkillMapper

import pandas as pd
import jieba
import json
import time

app = Flask(__name__)
kg = KnowledgeGraph()
search_manager = SearchManager()
search_manager_v2 = SearchManagerV2()
learning_path_sponsor = LearningPathSponsor()

@app.route('/uploadMaterial', methods=['POST'])
def upload_material():
    if request.method == 'POST':
        data = json.loads(request.data)
        kg.create_material_instance(data)
    return '上传素材成功'


@app.route('/addTeacher', methods=['POST'])
def add_teacher():
    if request.method == 'POST':
        data = json.loads(request.data)
        kg.create_teacher_instance(data)
    return '添加教师用户成功'


# 发布课程
@app.route('/publishLesson', methods=['POST'])
def add_lesson():  # 这里接收到工程数据然后逐层的进行解析并生成图谱数据
    if request.method == 'POST':
        # step1：保存工程数据——课程数据
        lesson_data = json.loads(request.data)
        kg.add_graph_data(lesson_data)
    return json.dumps({"status": "success"})


# 取消发布课程
@app.route('/unPublishLesson', methods=['POST'])
def delete_lesson():  # 这里接收到工程数据然后逐层的进行解析并生成图谱数据
    if request.method == 'POST':
        # step1：保存工程数据——课程数据
        lesson_data = json.loads(request.data)
        userid = lesson_data["userId"]
        if kg.check_lesson_existed(userid, lesson_data["_id"]):
            kg.delete_graph_data(lesson_data)
        else:
            return "课程不存在"
    return json.dumps({"status": "success"})


# 搜索教师信息
@app.route('/searchTeacher', methods=['GET'])
def search_teacher():  # 这里接收到工程数据然后逐层的进行解析并生成图谱数据
    if request.method == 'GET':
        # step1：保存工程数据——课程数据
        search_pattern = json.loads(request.data)
        results = search_manager.search_teacher(search_pattern)
        # 返回教师的id，并在非关系数据库中查找教师的信息
        return json.dumps({
            "status": "success",
            "result": results
        })
    return json.dumps({"status": "false"})


# 搜索课程信息
@app.route('/searchLesson', methods=['POST'])
def search_lesson():
    if request.method == 'POST':
        search_pattern = json.loads(request.data)
        results = search_manager.search_lesson(search_pattern)
        return json.dumps({
            "status": "success",
            "result": results
        })
    return json.dumps({"status": "false"})


# 全局下的知识点检索
@app.route('/searchKnowledge', methods=['POST'])
def search_knowledge():
    if request.method == 'POST':
        search_pattern = json.loads(request.data)
        extend_pattern = search_manager.match_knowledges_by_title(search_pattern)
        results = []
        for item in extend_pattern:
            results = search_manager.search_knowledge(item)
        return json.dumps({
            "status": "success",
            "result": results
        })
    return json.dumps({"status": "false"})


# 课程内的知识点检索
@app.route('/searchKnowledgeInLesson', methods=['POST'])
def search_knowledge_in_lesson():
    if request.method == 'POST':
        search_pattern = json.loads(request.data)
        # results = search_manager.search_knowledge(search_pattern)
        extend_pattern = search_manager.transform_title_to_id_in_lesson(search_pattern, search_pattern)
        results = []
        for item in extend_pattern:
            results.append(search_manager.search_knowledge(item))
        return json.dumps(results)
    return json.dumps({"status": "false"})


@app.route('/search', methods=['POST'])
def search():
    def _reinit_jieba(dict):
        jieba.initialize()
        for word in dict:
            jieba.suggest_freq(word, True)

    CALCULATE_TIME = True
    if CALCULATE_TIME:
        time_collector = {
            "knowledge": [],
            "lesson": [],
            "kunit": [],
            "mcourse": [],
            "acourse": [],
        }

    search_input = json.loads(request.data)["searchInput"]
    search_options = json.loads(request.data)["searchOptions"]
    search_dict = json.loads(request.data)["searchDict"]
    searched_ids = []
    search_patterns_set = {search_input}
    lesson_results = []
    knowledge_results = []
    kunit_results = []
    mcourse_results = []
    acourse_results = []

    if len(search_options) == 0:
        return jsonify({
            "status": "false",
            "message": "No SearchOptions!"
        })

    _reinit_jieba(search_dict)

    for pattern in jieba.cut_for_search(search_input):
        search_patterns_set.add(pattern)

    # 按长度降序排列
    search_patterns = list(search_patterns_set)
    search_patterns.sort(key=lambda ele: len(ele), reverse=True)

    for option in search_options:
        for search_pattern in search_patterns:

            # 计算搜索实际时间
            if CALCULATE_TIME:
                start_time = time.clock()

            if option == 'lesson':
                lesson_result = search_manager.search_lesson_info(search_pattern, searched_ids)
                if lesson_result:
                    lesson_results += lesson_result

            elif option == 'knowledge':
                # 搜知识点
                match_knowledges = search_manager.match_knowledges_by_title(search_pattern)
                # 获取每个知识点对应的所有匹配内容
                for item in match_knowledges:
                    if item in searched_ids:
                        continue
                    searched_ids.append(item)

                    knowledge_result = search_manager.search_knowledge(item)
                    if knowledge_result:
                        knowledge_results += knowledge_result

            elif option == 'kunit':
                match_kunits = search_manager.match_kunits_by_title(search_pattern)
                for item in match_kunits:
                    if item in searched_ids:
                        continue
                    searched_ids.append(item)
                    kunit_results.append(search_manager.get_direct_resources_with_kunit(item))

            elif option == 'mcourse':
                match_mcourses = search_manager.match_mcourses_by_title(search_pattern)
                for item in match_mcourses:
                    if item in searched_ids:
                        continue
                    searched_ids.append(item)
                    mcourse_results.append(search_manager.get_direct_resources_with_mcourse(item))

            elif option == 'acourse':
                match_acourses = search_manager.match_acourses_by_title(search_pattern)
                for item in match_acourses:
                    if item in searched_ids:
                        continue
                    searched_ids.append(item)
                    acourse_results.append(search_manager.get_direct_resources_with_acourse(item))

            if CALCULATE_TIME:
                end_time = time.clock()
                time_collector[option].append(round(end_time - start_time, 2))

    if CALCULATE_TIME:
        print(search_options)
        print(search_patterns)
        print(time_collector)

    return jsonify({
        "status": "success",
        "result": {
            "lesson": lesson_results,
            "knowledge": knowledge_results,
            "kunit": kunit_results,
            "mcourse": mcourse_results,
            "acourse": acourse_results
        }
    })


@app.route('/search-v2', methods=['POST'])
def search_v2():
    def _reinit_jieba(dict):
        jieba.initialize()
        for word in dict:
            jieba.suggest_freq(word, True)

    def _get_keywords_from(input):
        keywords_set = {input}

        for keyword in jieba.cut_for_search(input):
            keywords_set.add(keyword)

        # 按长度降序排列
        keywords = list(keywords_set)
        keywords.sort(key=lambda ele: len(ele), reverse=True)

        return keywords

    search_input = json.loads(request.data)["searchInput"]
    resource_types = [EducationalResourceType(value) for value in json.loads(request.data)["resourceTypes"]]
    search_dict = json.loads(request.data)["searchDict"]

    result = SearchResult()

    _reinit_jieba(search_dict)
    keywords = _get_keywords_from(search_input)

    for keyword in keywords:
        single_result = search_manager_v2.search(keyword, {"resource_types": resource_types}, result)
        result.merge(single_result)

    return jsonify({
        "status": "success",
        "result": result.to_json(),
    })

@app.route('/lessons', methods=['GET'])
def get_lessons_router_v2():
    search_result = SearchResult()
    for type in EducationalResourceType.getBasicTypes():
        resource_ids = request.args.get(type.value + "s").split(",")
        if len(resource_ids) > 0:
            search_result.merge(search_manager_v2.get_lessons_by_resources(type, resource_ids))

    return jsonify({
        "status": "success",
        "result": search_result.get(resource_type=EducationalResourceType.lesson),
    })

# 根据 id 获取课程
# 返回值：{
#     status: "success",
#     result: {
#         lesson: {},             # 当前知识点所属课程信息
#         knowledges: [{}, ...],   # 当前知识点一级关联知识点，当前知识点会有属性 current: true
#         kunit: {},              # 当前知识点下的学习单元
#         mcourse: {},            # 当前知识点下的主课时
#         acourses: [{}, ...],     # 当前知识点下的辅课时
#     }
# }
@app.route('/getKnowledge', methods=['POST'])
def get_knowledge():
    id = json.loads(request.data)["id"]
    if not id:
        return json.dumps({
            "status": "error",
            "message": "未传入知识点 ID!"
        })

    # 获取当前知识点的课程信息、下属教学单元、主辅课时
    lesson = search_manager.get_full_info_under_knowledge(id)
    # 获取当前知识点的直连知识点
    neighbor_knowledge = search_manager.get_neighbor_knowledge(id)
    # 合并成请求返回样式
    lesson["knowledge"]["id"] = id
    lesson["knowledge"]["current"] = True
    neighbor_knowledge.append(lesson["knowledge"])
    lesson["knowledge"] = neighbor_knowledge
    return jsonify({
        "status": "success",
        "result": lesson
    })
# 根据 id 获取教学单元
# 返回值：{
#     status: "success",
#     result: {
#         lesson: {},             # 当前知识点所属课程信息
#         knowledges: {}          # 当前知识点一级关联知识点，当前知识点会有属性 current: true
#         kunit: {},              # 当前知识点下的学习单元
#         mcourse: {},            # 当前知识点下的主课时
#         acourses: [{}, ...],    # 当前知识点下的辅课时
#     }
# }
@app.route('/getKunit', methods=['POST'])
def get_kunit():
    id = json.loads(request.data)["id"]
    if not id:
        return json.dumps({
            "status": "error",
            "message": "未传入 ID!"
        })

    kunit = search_manager.get_info_by_id(id, "kunit")
    return jsonify({
        "status": "success",
        "result": search_manager.get_direct_resources_with_kunit(kunit)
    })
@app.route('/getMcourse', methods=['POST'])
def get_mcourse():
    id = json.loads(request.data)["id"]
    if not id:
        return json.dumps({
            "status": "error",
            "message": "未传入 ID!"
        })

    mcourse = search_manager.get_info_by_id(id, "mcourse")
    return jsonify({
        "status": "success",
        "result": search_manager.get_direct_resources_with_mcourse(mcourse)
    })
@app.route('/getAcourse', methods=['POST'])
def get_Acourse():
    id = json.loads(request.data)["id"]
    if not id:
        return json.dumps({
            "status": "error",
            "message": "未传入 ID!"
        })

    acourse = search_manager.get_info_by_id(id, "acourse")
    return jsonify({
        "status": "success",
        "result": search_manager.get_direct_resources_with_acourse(acourse)
    })

# # 创建课程
# # 原则上不需要，先留着吧
# @app.route('/createLesson', methods=['POST'])
# def create_lesson():  # 用户创建课程
#     if request.method == 'POST':
#         # step1：保存工程数据——课程数据
#         lesson_data = json.loads(request.data)
#         kg.create_lesson_instance(lesson_data)
#     return '创建课程成功'

LEARNING_PATH_RECOMMENDATION_CONFIG = {
    'ASSISTment2009-2010': {
        'skill_data_path': 'learningPath/utils/sorted_skill.csv',
        'skill_name_column': 'skill_name_cn',
    }
}
@app.route('/learning-path-recommendation', methods=['POST'])
def learning_path_recommendation_router():
    request_data = json.loads(request.data)
    learning_history = request_data["learningHistory"]
    course_name = request_data["course"]

    if course_name not in LEARNING_PATH_RECOMMENDATION_CONFIG:
        return jsonify({
            "status": "error",
            "result": "不支持的课程！"
        })
    config = LEARNING_PATH_RECOMMENDATION_CONFIG[course_name]

    skill_data = pd.read_csv(config["skill_data_path"], encoding='gbk')
    skill_mapper = SkillMapper(skill_data, config["skill_name_column"])

    learning_history_with_serial = [[skill_mapper.name_to_serial(learn["name"]), learn["correct"]]
                                    for learn in learning_history
                                    if skill_mapper.name_to_serial(learn["name"]) is not None]

    recommendation_knowledge_serial = learning_path_sponsor.recommend(course_name, learning_history_with_serial)
    recommendation_knowledge = skill_mapper.serial_to_name(recommendation_knowledge_serial)
    return jsonify({
        "status": "success",
        "result": recommendation_knowledge
    })


@app.route('/knowledge-demands', methods=['POST'])
def get_knowledge_demands():
    request_data = json.loads(request.data)
    learning_history = request_data["learningHistory"]
    course_name = request_data["course"]

    if course_name not in LEARNING_PATH_RECOMMENDATION_CONFIG:
        return jsonify({
            "status": "error",
            "result": "不支持的课程！"
        })

    config = LEARNING_PATH_RECOMMENDATION_CONFIG[course_name]

    skill_data = pd.read_csv(config["skill_data_path"], encoding='gbk')
    skill_mapper = SkillMapper(skill_data, config["skill_name_column"])

    learning_history_with_serial = [[skill_mapper.name_to_serial(learn["name"]), learn["correct"]]
                                    for learn in learning_history
                                    if skill_mapper.name_to_serial(learn["name"]) is not None]

    """
    knowledge_demands_list: [ demand, demand, ...]
    knowledge_demands: { knowledge_name: demand, ... }
    """
    knowledge_demands_list = learning_path_sponsor.get_knowledge_demands(course_name, learning_history_with_serial)
    knowledge_demands = {skill_mapper.serial_to_name(serial): float(demand)
                         for serial, demand in enumerate(knowledge_demands_list)}
    return jsonify({
        "status": "success",
        "result": knowledge_demands
    })


if __name__ == '__main__':
    app.debug = True
    app.run()
