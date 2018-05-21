from SPARQLWrapper import SPARQLWrapper, JSON
from retrieved.searchOperate import SearchOperate


class SearchManager:
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
        #使用课程id和课程内知识点id进行检索
        result = self.get_search_result(lesson_id, knowledge_id)
        return result

    def get_search_result(self, lesson_id, knowledge_id):
        #获取课程的知识体系
        root_knowledge_id = self.get_root_knowledge(lesson_id)
        search_operate = SearchOperate(lesson_id, root_knowledge_id)

        #检索概念
        result = search_operate.get_result(knowledge_id)
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
