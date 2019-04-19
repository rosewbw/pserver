from SPARQLWrapper import SPARQLWrapper, JSON, POST
import re
import types


class KnowledgeGraph:
    # KnowledgeGraph 用于图谱数据的生成和释放
    def __init__(self):
        self.sqlstr_PREFIX = """
        PREFIX : <http://www.semanticweb.org/wbw/ontologies/2018/4/basic#> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl:   <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX basic: <http://www.semanticweb.org/wbw/ontologies/2018/4/basic#>
        PREFIX material: <http://www.semanticweb.org/wbw/ontologies/2018/4/material#>
        PREFIX knowledge: <http://www.semanticweb.org/wbw/ontologies/2018/4/knowledge#> 
        PREFIX course: <http://www.semanticweb.org/wbw/ontologies/2018/4/course#> 
        PREFIX lesson: <http://www.semanticweb.org/wbw/ontologies/2018/4/lesson#> 
        PREFIX teach: <http://www.semanticweb.org/wbw/ontologies/2018/4/teach#> 
        PREFIX teacher: <http://www.semanticweb.org/wbw/ontologies/2018/4/teacher#> 
        PREFIX student: <http://www.semanticweb.org/wbw/ontologies/2018/4/student#> 
        """

        self.sparql = SPARQLWrapper("http://localhost:3030/basic/query",
                                    updateEndpoint="http://localhost:3030/basic/update")

        self.data_predicate = {
            # 教学单元
            "teach": {
                "keyword": "teach:教学单元关键字",
                "description": "teach:教学单元描述",
                "title": "teach:教学单元名称",
            },
            # 知识点
            "knowledge": {
                "demand": "knowledge:大纲要求难度",
                "achieve": "knowledge:学生掌握程度",
                "title": "knowledge:知识点名称",
                "thumbnailUrl": "knowledge:知识点缩略图Url",
                "synonym": "knowledge:同义词",
                "difficulty": "knowledge:难度系数",
                "importance": "knowledge:重要程度",
                "description": "knowledge:描述信息",

            },
            # 资源
            "material": {
                "url": "material:资源位置",
                "userid": "material:上传者id",
                "size": "material:资源大小",
                "thumbnailUrl": "material:资源缩略图Url",
                "language": "material:资源语种",
                "keyword": "material:资源关键字",
                "description": "material:资源描述",
                "title": "material:资源名称",
                "applicableObject": "material:资源适用对象",
                "type": "material:资源类型",
                "duration": "material:资源时长"
            },
            # 课时
            "course": {
                "interactionDegree": "course:课时交互程度",
                "interactionType": "course:课时交互类型",
                "learningObjectType": "course:课时学习对象类型",
                "averageRetentionRate": "course:课时平均滞留率",
                "semanticDensity": "course:课时语义密度",
                "watchNum": "course:课时观看人数",
                "clickNum": "course:课时点击人数",
                "duration": "course:课时持续时间",
                "type": "course:课时类型",
                "difficulty": "course:课时难度",
                "typicalLearningTime": "course:课时典型学习时间",
                "title": "course:课时名称",
            },
            # 课程
            "lesson": {
                "title": "lesson:课程名称",
                "description": "lesson:课程描述信息",
                "thumbnailUrl": "lesson:课程缩略图",
                "publishStatus": "lesson:课程发布状态",
            },
            "teacher": {
                "studentNum": "teacher: 教师学生人数",
                "name": "teacher:教师姓名",
                "sex": "teacher:教师性别",
                "expertCourse": "teacher:教师擅长课程",
                "age": "teacher:教师年龄"
            },
            "student": {
                "name": "student:学生姓名",
                "age": "student:学生年龄",
                "sex": "student:学生性别",
                "email": "student:学生邮件地址",
                "school": "student:学生学校"
            },
            "relationship": {
                "hasChildNode": "basic:hasChildNode",
                "hasParentNode": "basic:hasParentNode",
                "hasParallelNode": "basic:hasParallelNode",
                "hasBrotherNode": "basic:hasBrotherNode",
                "hasRelyOnNode": "basic:hasRelyOnNode",
                "hasBeRelyByNode": "basic:hasBeRelyByNode",
                "hasNextNode": "basic:hasNextNode",
                "hasPrevNode": "basic:hasPrevNode",
                "hasSynonymNode": "basic:hasSynonymNode",
                "hasRelateNode": "basic:hasRelateNode",
            }
        }

    def parse_data_property(self, data_type, data_group):
        sqlstr_DATA = ''
        if '_id' in data_group.keys():
            _id = data_group["_id"]
            for key in data_group.keys():
                if key in self.data_predicate[data_type].keys():
                    if isinstance(data_group[key], list):
                        if len(data_group[key]) != 0:
                            for item in data_group[key]:
                                sqlstr_DATA += '{data_type}:{_id} {data_predicate} \"{data}\".\n'.format(
                                    data_type=data_type,
                                    _id=_id,
                                    data_predicate=self.data_predicate[data_type][key],
                                    data=item
                                )
                    else:
                        sqlstr_DATA += '{data_type}:{_id} {data_predicate} \"{data}\".\n'.format(
                            data_type=data_type,
                            _id=_id,
                            data_predicate=self.data_predicate[data_type][key],
                            data=data_group[key]
                        )
            return sqlstr_DATA
        else:
            return False

    def parse_object_property(self, data_group):
        sqlstr_DATA = ''
        if '_id' in data_group.keys():
            _id = data_group["_id"]
            for key in data_group.keys():
                if key in self.data_predicate['relationship']:
                    if len(data_group[key]) != 0:
                        for item in data_group[key]:
                            sqlstr_DATA += 'knowledge:{id} {data_predicate} knowledge:{item}.\n'.format(
                                id=_id,
                                data_predicate=self.data_predicate['relationship'][key],
                                item=item
                            )

        return sqlstr_DATA

    # 创建资源的实例
    def create_material_instance(self, data_group):  # data_group={名称、位置、关键字、描述、类型、id}
        sqlstr_INSERT_DATA_BASE = self.parse_data_property('material', data_group)

        KEYS = ["_id", "url", "size", "thumbnailUrl", "language", "duration", "keyword", "description", "title", "type"]
        for key in KEYS:
            if key not in data_group:
                data_group[key] = ""

        sqlstr_INSERT_DATA = 'material:{id} a  owl:NamedIndividual.\
                    material:{id} a basic:视频.\
                    material:{id} material:资源位置 \"{url}\".\
                    material:{id} material:资源大小 \"{size}\".\
                    material:{id} material:资源缩略图Url \"{thumbnail_url}\".\
                    material:{id} material:资源语种 \"{language}\".\
                    material:{id} material:资源时长 \"{duration}\".\
                    material:{id} material:资源关键字 \"{keyword}\".\
                    material:{id} material:资源描述 \"{description}\".\
                    material:{id} material:资源名称 \"{title}\".\
                    material:{id} material:资源类型 \"{type}\".'.format(id=data_group["_id"],
                                                                    url=data_group["url"],
                                                                    size=data_group["size"],
                                                                    thumbnail_url=data_group["thumbnailUrl"],
                                                                    language=data_group["language"],
                                                                    duration=data_group["duration"],
                                                                    keyword=data_group["keyword"],
                                                                    description=data_group["description"],
                                                                    title=data_group["title"] or "",
                                                                    type=data_group["type"]
                                                                    )
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            self.add_material_to_teacher(data_group["userId"], data_group["_id"])
            return True
        else:
            return False

    # 创建知识点实例
    def create_knowledge_instance(self, data_group):  # data_group={名称、位置、关键字、描述、类型、id}
        sqlstr_INSERT_DATA_BASE = 'knowledge:{id} a owl:NamedIndividual.\n \
                            knowledge:{id} a basic:知识点.\n'.format(
            id=data_group["_id"]
        )
        sqlstr_INSERT_DATA_BASE += self.parse_data_property('knowledge', data_group)
        synonym = ""
        if len(data_group["synonym"]) != 0:
            for item in data_group["synonym"]:
                synonym += 'knowledge:{id}  knowledge:同义词 \"{synonym}\". '.format(
                    id=data_group["_id"],
                    synonym=item
                )

        # knowledge:{id} knowledge:难度系数 \"{difficulty}\".\
        # knowledge:{id} knowledge:重要程度 \"{importance}\".\
        # difficulty = data_group["difficulty"],
        # importance = data_group["importance"],.\
        # knowledge:{id} knowledge:描述信息 \"{description}\"
        # description = data_group["description"],\

        sqlstr_INSERT_DATA = 'knowledge:{id} a  owl:NamedIndividual.\
                    knowledge:{id} a basic:知识点.\
                    knowledge:{id} knowledge:大纲要求难度 \"{demand}\".\
                    knowledge:{id} knowledge:学生掌握程度 \"{achieve}\".\
                    knowledge:{id} knowledge:知识点名称 \"{title}\".\
                    knowledge:{id} knowledge:知识点缩略图Url \"{thumbnail_url}\".'.format(
            id=data_group["_id"],
            demand=data_group["demand"],
            achieve=data_group["achieve"],
            title=data_group["title"],
            thumbnail_url=data_group["thumbnailUrl"],
        ) + synonym
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    # 创建教学单元实例
    def create_teach_instance(self, data_group):  # data_group={名称、位置、关键字、描述、类型、id}
        sqlstr_INSERT_DATA_BASE = self.parse_data_property('teach', data_group)
        sqlstr_INSERT_DATA_BASE += 'teach:{id} a  owl:NamedIndividual.\
                    teach:{id} a basic:教学单元.'.format(
            id=data_group["_id"],
        )
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA_BASE + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    # 创建课时实例
    def create_course_instance(self, data_group):  # data_group={名称、位置、关键字、描述、类型、id}

        sqlstr_INSERT_DATA_BASE = self.parse_data_property('course', data_group)
        # course: {id}
        # course: 课时典型学习时间 \"{typicalLearningTime}\".\
        # typicalLearningTime = data_group["typicalLearningTime"],
        sqlstr_INSERT_DATA = 'course:{id} a  owl:NamedIndividual.\
                    course:{id} a basic:课时.\
                    course:{id} course:课时交互程度 \"{interactionDegree}\".\
                    course:{id} course:课时交互类型 \"{interactionType}\".\
                    course:{id} course:课时学习对象类型 \"{learningObjectType}\".\
                    course:{id} course:课时平均滞留率 \"{averageRetentionRate}\".\
                    course:{id} course:课时语义密度 \"{semanticDensity}\".\
                    course:{id} course:课时观看人数 \"{watchNum}\".\
                    course:{id} course:课时点击人数 \"{clickNum}\".\
                    course:{id} course:课时持续时间 \"{duration}\".\
                    course:{id} course:课时类型 \"{type}\".\
                    course:{id} course:课时难度 \"{difficulty}\".\
                    course:{id} course:课时名称 \"{title}\".'.format(
            id=data_group["_id"],
            interactionDegree=data_group["interactionDegree"],
            interactionType=data_group["interactionType"],
            learningObjectType=data_group["learningObjectType"],
            averageRetentionRate=data_group["averageRetentionRate"],
            semanticDensity=data_group["semanticDensity"],
            watchNum=data_group["watchNum"],
            clickNum=data_group["clickNum"],
            duration=data_group["duration"],
            type=data_group["type"],
            difficulty=data_group["difficulty"],
            title=data_group["title"],

        )
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    # 创建课程单元实例
    def create_lesson_instance(self, data_group):  # data_group={名称、位置、关键字、描述、类型、id}
        sqlstr_INSERT_DATA = 'lesson:{id} a  owl:NamedIndividual.\
                    lesson:{id} a basic:课程.\
                    lesson:{id} lesson:课程名称 \"{title}\".\
                    lesson:{id} lesson:课程描述信息 \"{description}\".\
                    lesson:{id} lesson:课程发布状态 \"{publishStatus}\".\
                    lesson:{id} lesson:课程缩略图 \"{thumbnailUrl}\".'.format(
            id=data_group["_id"],
            title=data_group["projectName"],
            description=data_group["description"],
            publishStatus=data_group["publishStatus"],
            thumbnailUrl=data_group["thumbnailUrl"]
        )
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            self.add_lesson_to_teacher(data_group["userId"], data_group["_id"])
            return True
        else:
            return False

    def create_teacher_instance(self, data_group):
        sqlstr_INSERT_DATA = 'teacher:{id} a  owl:NamedIndividual.\
                    teacher:{id} a basic:教师.\
                    teacher:{id} teacher:教师学生人数 \"{studentNum}\".\
                    teacher:{id} teacher:教师姓名 \"{name}\".\
                    teacher:{id} teacher:教师性别 \"{sex}\".\
                    teacher:{id} teacher:教师擅长课程 \"{expertCourse}\".\
                    teacher:{id} teacher:教师年龄 \"{age}\".'.format(
            id=data_group["_id"],
            studentNum=data_group["studentNum"],
            name=data_group["name"],
            sex=data_group["sex"],
            expertCourse=data_group["expertCourse"],
            age=data_group["age"]
        )
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def create_student_instance(self, data_group):
        sqlstr_INSERT_DATA = 'student:{id} a  owl:NamedIndividual.\
                    student:{id} a basic:学生.\
                    student:{id} student:学生专业 \"{subject}\".\
                    student:{id} student:学生姓名 \"{name}\".\
                    student:{id} student:学生年龄 \"{age}\".\
                    student:{id} student:学生性别 \"{sex}\".\
                    student:{id} student:学生邮件地址 \"{email}\".\
                    student:{id} student:学生学校 \"{school}\".'.format(
            id=data_group["_id"],
            subject=data_group["subject"],
            name=data_group["name"],
            age=data_group["age"],
            sex=data_group["sex"],
            email=data_group["email"],
            school=data_group["school"],
        )
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_knowledge_to_lesson(self, lesson_id, knowledge_id):
        sqlstr_INSERT = """
        INSERT DATA{
        lesson:%s basic:hasKnowledge knowledge:%s.
        }
        """ % (lesson_id, knowledge_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def remove_knowledge_from_lesson(self, lesson_id, knowledge_id):
        sqlstr_DELETE = """
        DELETE {
        lesson:%s basic:hasKnowledge knowledge:%s.
        }
        """ % (lesson_id, knowledge_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_teach_to_knowledge(self, knowledge_id, teach_id):
        sqlstr_INSERT = """
        INSERT DATA{
        knowledge:%s basic:hasTeach teach:%s.
        }
        """ % (knowledge_id, teach_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_course_to_teach(self, teach_id, course_id, course_type):
        # 主课时
        if course_type == 'main':
            sqlstr_INSERT = """
            INSERT DATA{
            teach:%s basic:hasMCourse course:%s.
            }
            """ % (teach_id, course_id)
        # 辅课时
        else:
            sqlstr_INSERT = """
                    INSERT DATA{
                    teach:%s basic:hasACourse course:%s.
                    }
                    """ % (teach_id, course_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_material_to_course(self, course_id, material_id):
        sqlstr_INSERT = """
        INSERT DATA{
        course:%s basic:hasMaterial material:%s.
        }
        """ % (course_id, material_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def link_knowledges(self, knowledge_A_id, knowledge_B_id, relation_type):
        sqlstr_INSERT = """
        INSERT DATA{
        knowledge:%s basic:%s knowledge:%s.
        }
        """ % (knowledge_A_id, relation_type, knowledge_B_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def separate_knowledges(self, knowledge_A_id, knowledge_B_id, relation_type):
        sqlstr_DELETE = """
        DELETE{
        knowledge:%s basic:%s knowledge:%s.
        }
        """ % (knowledge_A_id, relation_type, knowledge_B_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_material_to_teacher(self, teacher_id, material_id):
        sqlstr_INSERT = """
        INSERT DATA{
        teacher:%s basic:hasUpload material:%s.
        }
        """ % (teacher_id, material_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def remove_material_from_teacher(self, teacher_id, material_id):
        sqlstr_DELETE = """
        DELETE{
        teacher:%s basic:hasUpload material:%s.
        }
        """ % (teacher_id, material_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_lesson_to_teacher(self, teacher_id, lesson_id):
        sqlstr_INSERT = """
        INSERT DATA{
        teacher:%s basic:hasCreateLesson lesson:%s.
        }
        """ % (teacher_id, lesson_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def remove_lesson_from_teacher(self, teacher_id, lesson_id):
        sqlstr_DELETE = """
        DELETE{
            teacher:%s basic:hasCreateLesson lesson:%s.
        }
        WHERE{
            teacher:%s basic:hasCreateLesson lesson:%s.
               }
        """ % (teacher_id, lesson_id, teacher_id, lesson_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_teach_to_teacher(self, teacher_id, teach_id):
        sqlstr_INSERT = """
        INSERT DATA{
        teacher:%s basic:hasCreateTeach teach:%s.
        }
        """ % (teacher_id, teach_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def remove_teach_from_teacher(self, teacher_id, teach_id):
        sqlstr_DELETE = """
        DELETE{
            teacher:%s basic:hasCreateTeach teach:%s.
        }
        WHERE{
            teacher:%s basic:hasCreateTeach teach:%s.
               }
        """ % (teacher_id, teach_id, teacher_id, teach_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_lesson_to_student(self, student_id, lesson_id):
        sqlstr_INSERT = """
        INSERT DATA{
        student:%s basic:hasLearningLesson lesson:%s.
        }
        """ % (student_id, lesson_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def remove_lesson_from_student(self, student_id, lesson_id):
        sqlstr_DELETE = """
        DELETE{
            student:%s basic:hasLearningLesson lesson:%s.
        }
        WHERE{
            student:%s basic:hasLearningLesson lesson:%s.
               }
        """ % (student_id, lesson_id, student_id, lesson_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_knowledge_to_teacher(self, teacher_id, knowledge_id):
        sqlstr_INSERT = """
        INSERT DATA{
        teacher:%s basic:hasCreateKnowledge knowledge:%s.
        }
        """ % (teacher_id, knowledge_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def remove_knowledge_from_teacher(self, teacher_id, knowledge_id):
        sqlstr_DELETE = """
        DELETE{
        teacher:%s basic:hasCreateKnowledge knowledge:%s.
        }
        WHERE{
        teacher:%s basic:hasCreateKnowledge knowledge:%s.
        }
        """ % (teacher_id, knowledge_id, teacher_id, knowledge_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_course_to_teacher(self, teacher_id, course_id):
        sqlstr_INSERT = """
        INSERT DATA{
        teacher:%s basic:hasCreateCourse course:%s.
        }
        """ % (teacher_id, course_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def remove_course_from_teacher(self, teacher_id, course_id):
        sqlstr_DELETE = """
        DELETE{
            teacher:%s basic:hasCreateCourse course:%s.
        }
         WHERE{
            teacher:%s basic:hasCreateCourse course:%s.
               }
        """ % (teacher_id, course_id, teacher_id, course_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def check_lesson_existed(self, user_id, lesson_id):
        sqlstr_SELECT = """
                SELECT ?lesson_id
                """
        sqlstr_WHERE = """
                WHERE {
                    teacher:%s basic:hasCreateLesson ?lesson_id.
                }
                """ % user_id  # 这个术语称为字符串格式化，记着了
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        if results["results"]["bindings"]:
            for item in results["results"]["bindings"]:
                if item["lesson_id"]["value"].split("#")[-1] == lesson_id:
                    return True
            return False
        else:
            return False

    def update_graph_data_property(self, property_id, property_type, property_data):
        sqlstr_INSERT = """
                DELETE { math:%s math:difficulty_is ?old }
                INSERT { math:%s math:difficulty_is %f }
                WHERE
                  { math:%s math:difficulty_is ?old.
                  }
                """ % (property_id, property_id, property_id, property_id)  # 将该视频id加入对应的知识点下，作为示例

        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        # self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        result = self.sparql.query().convert().decode("utf-8")
        if "Success" in result:
            return True
        else:
            return False

    def connect_knowledges(self, knowledge_id, kIds, type):

        sqlstr_INSERT = """
               INSERT DATA{
               teacher:%s basic:hasCreateKnowledge knowledge:%s.
               }
               """ % (knowledge_id, knowledge_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def sparql_request(self, request_str, type):
        self.sparql.setMethod(POST)
        self.sparql.setQuery(request_str)
        result = self.sparql.query().convert().decode("utf-8")
        if type == 'insert' or type == 'delete':
            if "Success" in result:
                return True
            else:
                return False
        elif type == 'retrieved':
            return result

    def remove_instance(self, instance_id, instance_type):
        sqlstr_DELETE = """
               DELETE {
                   %s:%s ?property  ?data.
               }
               WHERE{
                    %s:%s ?property  ?data.
               }
               """ % (instance_type, instance_id, instance_type, instance_id)
        if self.sparql_request(self.sqlstr_PREFIX + sqlstr_DELETE, 'delete'):
            return True
        else:
            return False

    def delete_graph_data(self, data_group):
        # 删除课程数据
        lesson_id = data_group["_id"]
        userid = data_group['userId']
        self.remove_instance(lesson_id, 'lesson')
        self.remove_lesson_from_teacher(userid, lesson_id)
        # 删除知识点数据
        knowledge_data = data_group["data"]
        for item in knowledge_data:
            knowledge_id = item['_id']
            self.remove_instance(knowledge_id, 'knowledge')
            self.remove_knowledge_from_teacher(userid, knowledge_id)
            # 删除教学单元数据
            teach_data = item['teachUnit']
            self.remove_instance(teach_data["_id"], 'teach')
            self.remove_teach_from_teacher(userid, teach_data["_id"])
            # 删除主课时数据
            mainCourse_data = teach_data["mCourseUnit"]
            if mainCourse_data:
                self.remove_instance(mainCourse_data["_id"], 'course')
                self.remove_course_from_teacher(userid, mainCourse_data["_id"])
            aidCouse_data = teach_data["aCourseUnit"]
            if aidCouse_data:
                for ac in aidCouse_data:
                    self.remove_instance(ac["_id"], 'course')
                    self.remove_course_from_teacher(userid, ac["_id"])
        return "success"

    def add_root_knowledge_to_lesson(self, lesson_id, knowledge_id):
        sqlstr_INSERT = """
           INSERT DATA{
           lesson:%s basic:hasRootKnowledge knowledge:%s.
           }
           """ % (lesson_id, knowledge_id)
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_object_property(self, data_group):
        sqlstr_INSERT_DATA = self.parse_object_property(data_group)
        sqlstr_INSERT = 'INSERT DATA{' + sqlstr_INSERT_DATA + "}"
        self.sparql.setMethod(POST)
        self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
        result = self.sparql.query().convert().decode("utf-8")  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        if "Success" in result:
            return True
        else:
            return False

    def add_graph_data(self, data_group):
        lesson_data = data_group
        userid = lesson_data["userId"]
        self.create_lesson_instance(lesson_data)
        # 添加知识点实例
        knowledge_data = lesson_data["data"]
        for k in knowledge_data:
            if k["root"] == True:
                self.add_root_knowledge_to_lesson(lesson_data["_id"], k["_id"])
            self.create_knowledge_instance(k)
            self.add_knowledge_to_lesson(lesson_data["_id"], k["_id"])
            self.add_knowledge_to_teacher(userid, k["_id"])
            self.add_object_property(k)
            # 添加教学单元
            teach = k["teachUnit"]
            self.create_teach_instance(teach)
            self.add_teach_to_knowledge(k["_id"], teach["_id"])
            self.add_teach_to_teacher(userid, teach["_id"])
            # 添加主课时
            mCourse = teach["mCourseUnit"]
            if mCourse:
                self.create_course_instance(mCourse)
                self.add_course_to_teach(teach["_id"], mCourse["_id"], mCourse["type"])
                self.add_course_to_teacher(userid, mCourse["_id"])
                material = mCourse["material"]
                if material:
                    self.create_material_instance(material)
                    self.add_material_to_course(mCourse["_id"], material["_id"])
            # 添加辅课时
            aCourse = teach["aCourseUnit"]
            if aCourse:
                for ac in aCourse:
                    self.create_course_instance(ac)
                    self.add_course_to_teach(teach["_id"], ac["_id"], ac["type"])
                    self.add_course_to_teacher(userid, ac["_id"])
                    material = ac["material"]
                    if material:
                        self.create_material_instance(material)
                        self.add_material_to_course(ac["_id"], material["_id"])
