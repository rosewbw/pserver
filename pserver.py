from flask import Flask, request, jsonify
from graph.knowledgeGraph import KnowledgeGraph
from retrieved.searchManager import SearchManager
import json

app = Flask(__name__)
kg = KnowledgeGraph()
search_manager = SearchManager()


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
        extend_pattern = search_manager.transform_title_to_id(search_pattern)
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
    if request.method == 'POST':
        search_pattern = json.loads(request.data)["searchInput"]
        search_options = json.loads(request.data)["searchOptions"]
        lesson_results = []
        knowledge_results = []
        if len(search_options) == 2 or len(search_options) == 0:
            # 全局搜知识点和课程
            # 搜课程
            lesson_results = search_manager.search_lesson_info(search_pattern)
            # 搜知识点
            extend_pattern = search_manager.transform_title_to_id(search_pattern)
            for item in extend_pattern:
                knowledge_results.append(search_manager.search_knowledge(item))
        else:
            if search_options[0] == 'Lesson':
                # 搜课程
                lesson_results = search_manager.search_lesson_info(search_pattern)
                # lesson_results = search_manager.search_lesson(search_pattern)
            if search_options[0] == 'Knowledge':
                extend_pattern = search_manager.transform_title_to_id(search_pattern)
                for item in extend_pattern:
                    knowledge_results.append(search_manager.search_knowledge(item))

        return json.dumps({
            "status": "success",
            "result": {
                "lesson": lesson_results,
                "knowledge": knowledge_results
            }
        })
    return json.dumps({"status": "false"})


# 根据 id 获取课程
# 返回值：{
#     status: "success",
#     result: {
#         lesson: {},             # 当前知识点所属课程信息
#         knowledge: [{}, ...],   # 当前知识点一级关联知识点，当前知识点会有属性 current: true
#         kunit: [{}, ...],       # 当前知识点下的学习单元
#         mcourse: [{}, ...],     # 当前知识点下的主课时
#         acourse: [{}, ...],     # 当前知识点下的辅课时
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

    lesson = search_manager.search_knowledge(id)
    return jsonify({
        "status": "success",
        "result": lesson,
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


if __name__ == '__main__':
    app.debug = True
    app.run()
