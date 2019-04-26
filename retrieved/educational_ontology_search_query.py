import re
from enum import Enum
from custom_types import EducationalResourceType
from SPARQLWrapper import SPARQLWrapper, JSON


sparql = SPARQLWrapper("http://localhost:3030/basic/query",
                       updateEndpoint="http://localhost:3030/basic/update")
sparql.setReturnFormat(JSON)

sqlstr_PREFIX = """
        PREFIX : <http://www.semanticweb.org/wbw/ontologies/2018/4/basic#> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl:   <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX basic: <http://www.semanticweb.org/wbw/ontologies/2018/4/basic#>
        PREFIX material: <http://www.semanticweb.org/wbw/ontologies/2018/4/material#>
        PREFIX knowledge: <http://www.semanticweb.org/wbw/ontologies/2018/4/knowledge#> 
        PREFIX course: <http://www.semanticweb.org/wbw/ontologies/2018/4/course#> 
        PREFIX mcourse: <http://www.semanticweb.org/wbw/ontologies/2018/4/course#> 
        PREFIX acourse: <http://www.semanticweb.org/wbw/ontologies/2018/4/course#> 
        PREFIX lesson: <http://www.semanticweb.org/wbw/ontologies/2018/4/lesson#> 
        PREFIX kunit: <http://www.semanticweb.org/wbw/ontologies/2018/4/teach#> 
        PREFIX teach: <http://www.semanticweb.org/wbw/ontologies/2018/4/teach#> 
        PREFIX teacher: <http://www.semanticweb.org/wbw/ontologies/2018/4/teacher#> 
        PREFIX student: <http://www.semanticweb.org/wbw/ontologies/2018/4/student#> 
        """

data_predicate = {
    # 教学单元
    EducationalResourceType.kunit: {
        "keyword": "teach:教学单元关键字",
        "description": "teach:教学单元描述",
        "title": "teach:教学单元名称",
    },
    # 知识点
    EducationalResourceType.knowledge: {
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
    EducationalResourceType.mcourse: {
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
    # 辅课时
    EducationalResourceType.acourse: {
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
    EducationalResourceType.lesson: {
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


class EducationalOntologySearchQuery(object):
    class ResultDataType(Enum):
        id = "id"
        info = "info"

    def __init__(self):
        self._query_ids = set()
        self._query_keywords = set()
        self._query_resource_type = None

        self._result_resource_type = None
        self._result_data_type = None
        self._with_related_search_resources = False

    def set_query_resource_type(self, resource_type):
        if resource_type in EducationalResourceType:
            self._query_resource_type = resource_type
        return self

    def set_query_ids(self, ids):
        self._query_ids = set(ids)
        return self

    def set_query_id(self, id):
        self._query_ids = {id}
        return self

    def set_query_keywords(self, keywords):
        self._query_keywords = set(keywords)
        return self

    def set_query_keyword(self, keyword):
        self._query_keywords = {keyword}
        return self

    def set_result_resource_type(self, resource_type):
        if resource_type in EducationalResourceType:
            self._result_resource_type = resource_type
        return self

    def set_result_data_type(self, result_type):
        if result_type in EducationalOntologySearchQuery.ResultDataType:
            self._result_data_type = result_type
        return self

    def set_with_related_search_resources(self, value=True):
        if isinstance(value, bool):
            self._with_related_search_resources = value
        return self

    def _parse_from_spasql_response(self, response):
        def _parse_response_key(content):
            for key, predicate in data_predicate[self._result_resource_type].items():
                if re.search(content, predicate):
                    return key
            raise ValueError("找不到 {} 对应的 predicate!".format(content))

        def _get_value(content):
            """
            针对 bindings 中每 item 的项，提取值
            当类型为 uri 时，切割 uri，返回 '#' 后的部分
            否则直接返回 value
            """
            if ("type" not in content) or ("value" not in content):
                return content
            if content["type"] == "uri":
                return content["value"].split('#')[-1]
            else:
                return content["value"]

        vars = response["head"]["vars"]
        bindings = response["results"]["bindings"]

        if self._result_data_type == EducationalOntologySearchQuery.ResultDataType.id:
            return [_get_value(item["{}_id".format(self._result_resource_type.value)]) for item in bindings]

        elif self._result_data_type == EducationalOntologySearchQuery.ResultDataType.info:
            result = []
            result_aggregated_by_id = {}

            for item in bindings:
                result_resource_type_id = _get_value(item["{}_id".format(self._result_resource_type.value)])
                query_resource_type_id = _get_value(item["{}_id".format(self._query_resource_type.value)])
                key = _parse_response_key(_get_value(item["key"]))
                value = _get_value(item["value"])

                if result_resource_type_id not in result_aggregated_by_id:
                    result_aggregated_by_id[result_resource_type_id] = {}

                result_aggregated_by_id[result_resource_type_id][key] = value

                if self._with_related_search_resources:
                    if "relatedSearchResources" not in result_aggregated_by_id[result_resource_type_id]:
                        result_aggregated_by_id[result_resource_type_id]["relatedSearchResources"] = {}

                    if self._query_resource_type.value + "s" not in result_aggregated_by_id[result_resource_type_id]["relatedSearchResources"]:
                        result_aggregated_by_id[result_resource_type_id]["relatedSearchResources"][self._query_resource_type.value + "s"] = [query_resource_type_id]
                    elif query_resource_type_id not in result_aggregated_by_id[result_resource_type_id]["relatedSearchResources"][self._query_resource_type.value + "s"]:
                        result_aggregated_by_id[result_resource_type_id]["relatedSearchResources"][self._query_resource_type.value + "s"].append(query_resource_type_id)

            for result_resource_type_id, item in result_aggregated_by_id.items():
                item["id"] = result_resource_type_id
                result.append(item)

            return result

        else:
            return bindings

    def exec(self):
        def _generate_select_str():
            if self._result_data_type == EducationalOntologySearchQuery.ResultDataType.id:
                return """
                SELECT ?{result_resource_type}_id
                """.format(result_resource_type=self._result_resource_type.value)
            elif self._result_data_type == EducationalOntologySearchQuery.ResultDataType.info:
                return """
                SELECT ?{result_resource_type}_id ?key ?value ?{query_resource_type}_id
                """.format(result_resource_type=self._result_resource_type.value,
                           query_resource_type=self._query_resource_type.value)
            else:
                raise ValueError("不支持的 ResultDataType: {}!".format(self._result_data_type))

        def _generate_where_str():
            def _generate_relation_part():
                if self._query_resource_type == self._result_resource_type:
                    return ""

                # FIXME: 这里可以使用无向图最短路径算法进行改进
                # 其中一个为 lesson
                if self._query_resource_type == EducationalResourceType.lesson or self._result_resource_type == EducationalResourceType.lesson:
                    another_resource_type = self._result_resource_type if self._query_resource_type == EducationalResourceType.lesson else self._query_resource_type
                    if another_resource_type == EducationalResourceType.knowledge:
                        return """
                        ?lesson_id basic:hasKnowledge ?knowledge_id .
                        """
                    elif another_resource_type == EducationalResourceType.kunit:
                        return """
                        ?lesson_id basic:hasKnowledge ?knowledge_id .
                        ?knowledge_id basic:hasTeach ?kunit_id .
                        """
                    elif another_resource_type == EducationalResourceType.mcourse:
                        return """
                        ?lesson_id basic:hasKnowledge ?knowledge_id .
                        ?knowledge_id basic:hasTeach ?kunit_id .
                        ?kunit_id basic:hasMCourse ?mcourse_id .
                        """
                    elif another_resource_type == EducationalResourceType.acourse:
                        return """
                        ?lesson_id basic:hasKnowledge ?knowledge_id .
                        ?knowledge_id basic:hasTeach ?kunit_id .
                        ?kunit_id basic:hasACourse ?acourse_id .
                        """
                # 其中一个为 knowledge
                elif self._query_resource_type == EducationalResourceType.knowledge or self._result_resource_type == EducationalResourceType.knowledge:
                    another_resource_type = self._result_resource_type if self._query_resource_type == EducationalResourceType.knowledge else self._query_resource_type
                    if another_resource_type == EducationalResourceType.kunit:
                        return """
                            ?knowledge_id basic:hasTeach ?kunit_id .
                            """
                    elif another_resource_type == EducationalResourceType.mcourse:
                        return """
                            ?knowledge_id basic:hasTeach ?kunit_id .
                            ?kunit_id basic:hasMCourse ?mcourse_id .
                            """
                    elif another_resource_type == EducationalResourceType.acourse:
                        return """
                            ?knowledge_id basic:hasTeach ?kunit_id .
                            ?kunit_id basic:hasACourse ?acourse_id .
                            """
                # 其中一个为 kunit
                elif self._query_resource_type == EducationalResourceType.kunit or self._result_resource_type == EducationalResourceType.kunit:
                    another_resource_type = self._result_resource_type if self._query_resource_type == EducationalResourceType.kunit else self._query_resource_type
                    if another_resource_type == EducationalResourceType.mcourse:
                        return """
                            ?kunit_id basic:hasMCourse ?mcourse_id .
                            """
                    elif another_resource_type == EducationalResourceType.acourse:
                        return """
                            ?kunit_id basic:hasACourse ?acourse_id .
                            """
                # 只可能一个为 mcourse 一个为 acourse
                else:
                    return """
                        ?kunit_id basic:hasMCourse ?mcourse_id .
                        ?kunit_id basic:hasACourse ?acourse_id .
                        """

            def _generate_query_part():
                if len(self._query_ids) == 0 and len(self._query_keywords) == 0:
                    raise ValueError("id 和 keyword 至少有一项不为 0!")

                query_part = ""
                if len(self._query_ids) > 0:
                    query_part += """
                    VALUES ?{query_resource_type}_id {{ {query_ids} }}
                    """.format(query_resource_type=self._query_resource_type.value,
                               query_ids=" ".join(["{}:{}".format(self._query_resource_type.value, id)
                                                   for id in self._query_ids]))

                if len(self._query_keywords) > 0:
                    query_part += """
                    ?{query_resource_type}_id {title_relation} ?{query_resource_type}_title .
                    FILTER regex(?{query_resource_type}_title, ?keyword, "i")
                    VALUES ?keyword {{ {keywords} }}
                    """.format(query_resource_type=self._query_resource_type.value,
                               title_relation=data_predicate[self._query_resource_type]["title"],
                               keywords=" ".join("'{}'".format(keyword) for keyword in self._query_keywords))

                return query_part

            def _generate_result_part():
                if self._result_data_type == EducationalOntologySearchQuery.ResultDataType.info:
                    return """
                    ?{result_resource_type}_id ?key ?value .
                    VALUES ?key {{ {info_keys} }}
                    """.format(result_resource_type=self._result_resource_type.value,
                               info_keys=" ".join(data_predicate[self._result_resource_type].values()))

                return ""

            where_str = """
            WHERE {{
                {relation_part}
                
                {query_part}
                
                {result_part}
            }}
            """.format(relation_part=_generate_relation_part(),
                       query_part=_generate_query_part(),
                       result_part=_generate_result_part())
            return where_str

        # FIXME: root_knowledge 额外处理，非常丑了...
        if self._result_resource_type == EducationalResourceType.root_knowledge:
            search_query = """
            SELECT ?knowledge_id
            
            WHERE {{
                ?lesson_id basic:hasRootKnowledge ?knowledge_id
                VALUES ?lesson_id {{ {lesson_ids} }}
            }}
            """.format(lesson_ids=" ".join(["{}:{}".format(self._query_resource_type.value, id)
                                            for id in self._query_ids]))
            # 转换 result_resource_type 使后面能正常解析
            self._result_resource_type = EducationalResourceType.knowledge
        else:
            search_query = """
            {select_str}
            
            {where_str}
            """.format(select_str=_generate_select_str(),
                       where_str=_generate_where_str())

        response = self._request_spasql_endpoint(search_query)
        return self._parse_from_spasql_response(response)

    def _request_spasql_endpoint(self, search_query):
        sparql.setQuery(sqlstr_PREFIX + search_query)
        return sparql.query().convert()

