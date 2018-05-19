from flask import Flask, request
from knowledgeGraph import KnowledgeGraph
import uuid
import json
import os

app = Flask(__name__)
kg = KnowledgeGraph()


@app.route('/uploadMaterial', methods=['POST'])
def upload_material():
    if request.method == 'POST':
        data = json.loads(request.data)
        kg.create_material_instance(data)
    return 'success'


@app.route('/addTeacher', methods=['POST'])
def add_teacher():
    if request.method == 'POST':
        data = json.loads(request.data)
        kg.create_teacher_instance(data)
    return 'success'


# 保存课程
@app.route('/saveLesson', methods=['POST'])
def add_lesson():  # 这里接收到工程数据然后逐层的进行解析并生成图谱数据
    if request.method == 'POST':
        # step1：保存工程数据——课程数据
        lesson_data = json.loads(request.data)
        userid = lesson_data["userId"]
        if kg.check_lesson_existed(userid, lesson_data["_id"]):
            # 添加知识点实例
            knowledge_data = lesson_data["data"]
            for k in knowledge_data:
                kg.create_knowledge_instance(k)
                kg.add_knowledge_to_lesson(lesson_data["_id"], k["id"])
                kg.add_knowledge_to_teacher(userid, k["id"])
                # 添加教学单元
                teach = k["teachUnit"]
                kg.create_teach_instance(teach)
                kg.add_teach_to_knowledge(k["id"], teach["id"])
                kg.add_teach_to_teacher(userid, teach["id"])
                # 添加主课时
                mCourse = teach["mCourseUnit"]
                if mCourse:
                    kg.create_course_instance(mCourse)
                    kg.add_course_to_teach(teach["id"], mCourse["id"], mCourse["type"])
                    kg.add_course_to_teacher(userid, mCourse["id"])
                    material = mCourse["material"]
                    if material:
                        kg.add_material_to_course(mCourse["id"], material["_id"])
                # 添加辅课时
                aCourse = teach["aCourseUnit"]
                if aCourse:
                    for ac in aCourse:
                        kg.create_course_instance(ac)
                        kg.add_course_to_teach(teach["id"], ac["id"], ac["type"])
                        kg.add_course_to_teacher(userid, ac["id"])
                        material = ac["material"]
                        if material:
                            kg.add_material_to_course(ac["id"], material["_id"])
        else:
            return "课程不存在"
    return 'success'


# 创建课程
@app.route('/createLesson', methods=['POST'])
def create_lesson():  # 用户创建课程
    if request.method == 'POST':
        # step1：保存工程数据——课程数据
        lesson_data = json.loads(request.data)
        kg.create_lesson_instance(lesson_data)
    return 'success'


if __name__ == '__main__':
    app.debug = True
    app.run()
