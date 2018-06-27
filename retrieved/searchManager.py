from SPARQLWrapper import SPARQLWrapper, JSON
from retrieved.searchOperate import SearchOperate


class SearchManager:
    # SearchManager 用于检索的管理
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

    def search_request(self, search_query):
        self.sparql.setQuery(search_query)  # 这一步编辑查询语句
        self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
        results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
        # 查询请求，通过JSON格式接受返回的数据，存入results中
        result = []
        for item in results["results"]["bindings"]:
            temp = {}
            for key in item.keys():
                temp.setdefault(key, item[key]["value"].split("#")[-1])
            result.append(temp)
        return result

    def search_teacher(self, teacher_name):
        sqlstr_SELECT = """
                SELECT ?teacher_id
                """
        sqlstr_WHERE = """
                WHERE {
                    ?teacher_id teacher:教师姓名 %s.
                }
                """ % teacher_name  # 这个术语称为字符串格式化，记着了
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        return result

    def search_teacher_by_lesson(self, lesson_id):
        sqlstr_SELECT = """
                        SELECT ?teacher_name
                        """
        sqlstr_WHERE = """
                        WHERE {
                            ?teacher_id basic:hasCreateLesson lesson:%s.
                            ?teacher_id teacher:教师姓名 ?teacher_name
                        }
                        """ % lesson_id  # 这个术语称为字符串格式化，记着了
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        return result

    def search_lesson(self, lesson_title):
        sqlstr_SELECT = """
                SELECT ?lesson_id ?description
                """
        sqlstr_WHERE = """
                WHERE {
                    ?lesson_id lesson:课程名称 \"%s\".
                }
                """ % lesson_title  # 这个术语称为字符串格式化，记着了

        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        return result

    def transform_title_to_id(self, knowledge_title):
        synonym_extend = self.extend_by_synonym(knowledge_title)
        sqlstr_SELECT = """
                SELECT DISTINCT ?knowledge_id 
                """
        sqlstr_WHERE = """
                WHERE {
                    ?knowledge_id knowledge:知识点名称 \"%s\".
                }
                """ % knowledge_title
        results = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE) + synonym_extend
        result = []
        for item in results:
            result.append(item["knowledge_id"])
        result = list(set(result))
        return result

    def extend_by_synonym(self, knowledge_title):
        sqlstr_SELECT = """
                SELECT DISTINCT ?knowledge_id 
                """
        sqlstr_WHERE = """
                WHERE {
                    ?knowledge_id  knowledge:同义词 \"%s\".
                }
                """ % knowledge_title
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        return result

    def transform_title_to_id_in_lesson(self, lesson_id, knowledge_title):
        matches = self.transform_title_to_id(knowledge_title)
        for item in matches:
            if self.check_knowledge_in_lesson(lesson_id, item):
                return item

    def check_knowledge_in_lesson(self, lesson_id, knowledge_id):
        sqlstr_SELECT = """
                       SELECT  ?lesson_id 
                       """
        sqlstr_WHERE = """
                       WHERE {
                           ?lesson_id  basic:hasKnowledge knowledge:%s.
                       }
                       """ % knowledge_id
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        if result[0]["lesson_id"] == lesson_id:
            return True
        else:
            return False

    def search_knowledge(self, knowledge_id):
        # 获取课程的id
        sqlstr_SELECT = """
               SELECT  ?lesson_id 
               """
        sqlstr_WHERE = """
               WHERE {
                   ?lesson_id  basic:hasKnowledge knowledge:%s.
               }
               """ % knowledge_id
        lesson_id = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)[0]["lesson_id"]
        if not lesson_id:
            return False
        # 使用课程id和课程内知识点id进行检索
        result = self.get_search_result(lesson_id, knowledge_id)
        return result

    def get_search_result(self, lesson_id, knowledge_id):
        # 获取课程的知识体系
        root_knowledge_id = self.get_root_knowledge(lesson_id)
        search_operate = SearchOperate(lesson_id, root_knowledge_id)
        # 检索概念
        knowledge_collection = search_operate.get_result(knowledge_id)
        # 检索概念匹配的教学单元、课时和资源
        result = self._get_full_info(knowledge_collection)
        return result

    def get_root_knowledge(self, lesson_id):
        sqlstr_SELECT = """
               SELECT  ?knowledge_id 
               """
        sqlstr_WHERE = """
               WHERE {
                   lesson:%s basic:hasRootKnowledge ?knowledge_id.
               }
               """ % lesson_id
        knowledge_id = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)[0]["knowledge_id"]
        return knowledge_id

    def _get_full_info(self, knowledge_collection):
        # 查找知识点对应的教学单元信息
        results = []
        for item in knowledge_collection:
            collection = {}
            collection.setdefault('similarity', item["similarity"])
            knowledge_id = item["knowledge_id"]

            lesson_id = self._get_lesson_id(knowledge_id)
            lesson_info = self._search_data_property(lesson_id, 'lesson')
            collection.setdefault('lesson', {
                'id': lesson_id,
                'data': lesson_info
            })

            knowledge_info = self._search_data_property(knowledge_id, 'knowledge')
            collection.setdefault('knowledge', {
                'id': knowledge_id,
                'data': knowledge_info
            })
            # 查找知识点对应的教学单元信息
            teach_id = self._get_teach_id(knowledge_id)
            teach_info = self._search_data_property(teach_id, 'teach')
            collection.setdefault('teach', {
                'id': teach_id,
                'data': teach_info
            })
            # 查找教学单元对应的主课时信息
            mcourse_id = self._get_mcourse_id(teach_id)
            mcourse_info = self._search_data_property(mcourse_id, 'course')
            # 查找主课时对应的资源信息
            material_id = self._get_material_id(mcourse_id)
            material_info = self._search_data_property(material_id, 'material')
            mcourse_info.setdefault('material_data', {
                'id': material_id,
                'data': material_info
            })
            # mcourse_info.setdefault('material_id', material_id)
            # mcourse_info.setdefault('mcourse_info', material_info)
            collection.setdefault('mcourse', {
                'id': mcourse_id,
                'data': mcourse_info
            })

            acourse_ids = self._get_acourse_id(teach_id)
            ac_info = []
            for a in acourse_ids:
                acourse_info = self._search_data_property(a['acourse_id'], 'course')
                material_id = self._get_material_id(a['acourse_id'])
                material_info = self._search_data_property(material_id, 'material')
                acourse_info.setdefault('material_data', {
                    'id': material_id,
                    'data': material_info
                })
                ac_info.append({
                    'id': a['acourse_id'],
                    'data': acourse_info
                })

            collection.setdefault('acourse', ac_info)
            results.append(collection)
        # 查找课时对应的资源信息
        return results

    def _get_teach_id(self, knowledge_id):
        sqlstr_SELECT = """
                SELECT ?teach_id 
                """
        sqlstr_WHERE = """
                WHERE {
                    knowledge:%s  basic:hasTeach ?teach_id.
                }
                """ % knowledge_id
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)[0]["teach_id"]
        return result

    def _get_lesson_id(self, knowledge_id):
        sqlstr_SELECT = """
                SELECT ?lesson_id 
                """
        sqlstr_WHERE = """
                WHERE {
                    ?lesson_id  basic:hasKnowledge knowledge:%s.
                }
                """ % knowledge_id
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)[0]["lesson_id"]
        return result

    def _get_mcourse_id(self, course_id):
        sqlstr_SELECT = """
                   SELECT ?mcourse_id 
                   """
        sqlstr_WHERE = """
                   WHERE {
                       teach:%s  basic:hasMCourse ?mcourse_id.
                   }
                   """ % course_id
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        if result:
            return result[0]['mcourse_id']
        else:
            return ''

    def _get_acourse_id(self, course_id):
        sqlstr_SELECT = """
               SELECT ?acourse_id 
               """
        sqlstr_WHERE = """
               WHERE {
                   teach:%s  basic:hasACourse ?acourse_id.
               }
               """ % course_id
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        if len(result) == 0:
            return []
        else:
            temp = []
            for i in result:
                temp.append(i)
            return temp

    def _get_material_id(self, course_id):
        sqlstr_SELECT = """
               SELECT ?material_id 
               """
        sqlstr_WHERE = """
               WHERE {
                   course:%s  basic:hasMaterial ?material_id.
               }
               """ % course_id
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        if result:
            return result[0]['material_id']
        else:
            return ''

    def _search_data_property(self, node_id, search_type):
        data_property = {}
        if self.data_predicate[search_type]:
            for key in self.data_predicate[search_type]:
                data_property.setdefault(key, self._search_data_property_func(node_id, search_type,
                                                                              self.data_predicate[search_type][key]))
        return data_property

    def _search_data_property_func(self, node_id, node_type, data_predicate):
        sqlstr_SELECT = """
                SELECT ?data 
                """
        sqlstr_WHERE = """
                WHERE {
                    %s:%s  %s ?data.
                }
                """ % (node_type, node_id, data_predicate)
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)
        if len(result) == 1:
            return result[0]["data"]
        elif len(result) == 0:
            return ''
        else:
            temp = []
            for i in result:
                temp.append(i)
            return temp

    def search_lesson_info(self, search_pattern):
        result = []
        lesson_id = self.search_lesson(search_pattern)
        for item in lesson_id:
            collection = {}
            teacher_name = self.search_teacher_by_lesson(item['lesson_id'])
            lesson_info = self._search_data_property(item['lesson_id'], 'lesson')
            collection.setdefault('lesson', {
                'id': item['lesson_id'],
                'data': lesson_info,
                'teacher_name': teacher_name
            })
            result.append(collection)
        return result
