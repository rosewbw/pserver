from flask import Flask, request
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

    return '创建课程图谱成功'


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
    return '删除课程图谱成功'


# 搜索教师信息
@app.route('/searchTeacher', methods=['GET'])
def search_teacher():  # 这里接收到工程数据然后逐层的进行解析并生成图谱数据
    if request.method == 'GET':
        # step1：保存工程数据——课程数据
        search_pattern = json.loads(request.data)
        results = search_manager.search_teacher(search_pattern)
        # 返回教师的id，并在非关系数据库中查找教师的信息
        return results
    return 404


# 搜索课程信息
@app.route('/searchLesson', methods=['GET'])
def search_lesson():
    if request.method == 'GET':
        search_pattern = request.args.get('searchPattern')
        results = search_manager.search_lesson(search_pattern)
        return json.dumps(results)
    return 404


#全局下的知识点检索
@app.route('/searchKnowledge', methods=['GET'])
def search_knowledge():
    if request.method == 'GET':
        search_pattern = request.args.get('searchPattern')
        extend_pattern = search_manager.transform_title_to_id(search_pattern)
        results = []
        for item in extend_pattern:
            results = search_manager.search_knowledge(item)
        return json.dumps(results)
    return 404


#课程内的知识点检索
@app.route('/searchKnowledgeInLesson', methods=['GET'])
def search_knowledge_in_lesson():
    if request.method == 'GET':
        search_pattern = request.args.get('searchPattern')
        # results = search_manager.search_knowledge(search_pattern)
        extend_pattern = search_manager.transform_title_to_id_in_lesson(search_pattern,search_pattern)
        results = []
        for item in extend_pattern:
            results = search_manager.search_knowledge(item)
        return json.dumps(results)
    return 404

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
