from collections import OrderedDict
from SPARQLWrapper import SPARQLWrapper, JSON

from custom_types import EducationalResourceType, KnowledgeRelationship
from retrieved.educational_ontology_search_query import EducationalOntologySearchQuery
from retrieved.knowledge_node import KnowledgeNode as Node


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


class KnowledgeRelationshipQuery(object):
    @classmethod
    def _request_spasql_endpoint(cls, search_query):
        sparql.setQuery(sqlstr_PREFIX + search_query)
        return sparql.query().convert()

    @classmethod
    def _parse_from_spasql_response(cls, response, has_origin_knowledge=False):
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

        result = {}
        if has_origin_knowledge:
            for item in bindings:
                target_knowledge_id = _get_value(item["target_knowledge_id"])
                relationship = KnowledgeRelationship.parse(_get_value(item["relationship"]))

                if relationship not in result:
                    result[relationship] = []

                result[relationship].append(target_knowledge_id)
        else:
            for item in bindings:
                target_knowledge_id = _get_value(item["target_knowledge_id"])
                relationship = KnowledgeRelationship.parse(_get_value(item["relationship"]))
                origin_knowledge_id = _get_value(item["origin_knowledge_id"])

                if origin_knowledge_id not in result:
                    result[origin_knowledge_id] = {relationship: [target_knowledge_id]}
                elif relationship not in result[origin_knowledge_id]:
                    result[origin_knowledge_id][relationship] = [target_knowledge_id]
                else:
                    result[origin_knowledge_id][relationship].append(target_knowledge_id)

        return result

    def __init__(self, lesson_id):
        self._lesson_id = lesson_id
        self._knowledge_id = None
        self._relationships = []

    def set_knowledge_id(self, knowledge_id):
        self._knowledge_id = knowledge_id

    def set_relationships(self, relationships):
        self._relationships = relationships

    def add_relationships(self, relationships):
        self._relationships += relationships

    def exec(self):
        """
        根据设定的知识点与相关关系进行检索

        Returns:
            设置了 _knowledge_id：
                {relationship: [target_knowledge_id, ...], ...}
            未设置 _knowledge_id：
                {knowledge_id: {relationship: [target_knowledge_id, ...], ...}, ...}
        """
        if not isinstance(self._relationships, list) or len(self._relationships) < 1:
            self._relationships = [rs for rs in KnowledgeRelationship]

        def _generate_select_str():
            if self._knowledge_id is None:
                return """
                SELECT ?target_knowledge_id ?relationship ?origin_knowledge_id
                """
            else:
                return """
                SELECT ?target_knowledge_id ?relationship
                """

        def _generate_where_str():
            if self._knowledge_id is None:
                return """
                WHERE {{
                    lesson:{lesson_id} basic:hasKnowledge ?origin_knowledge_id .
                    ?origin_knowledge_id ?relationship ?target_knowledge_id .
                    VALUES ?relationship {{ {relationships} }}
                }}
                """.format(lesson_id=self._lesson_id,
                           relationships=" ".join([rs.value for rs in self._relationships]))
            else:
                return """
                WHERE {{
                    lesson:{lesson_id} basic:hasKnowledge knowledge:{knowledge_id} .
                    knowledge:{knowledge_id} ?relationship ?target_knowledge_id .
                    VALUES ?relationship {{ {relationships} }}
                }}
                """.format(lesson_id=self._lesson_id,
                           knowledge_id=self._knowledge_id,
                           relationships=" ".join([rs.value for rs in self._relationships]))

        search_query = """
        {select_str}
        
        {where_str}
        """.format(select_str=_generate_select_str(),
                   where_str=_generate_where_str())

        response = self.__class__._request_spasql_endpoint(search_query)
        return self.__class__._parse_from_spasql_response(response, self._knowledge_id is not None)


class KnowledgeTree(object):
    root_depth = 1

    @classmethod
    def get_root_id_by_lesson_id(cls, lesson_id):
        root_ids = EducationalOntologySearchQuery() \
            .set_query_resource_type(EducationalResourceType.lesson) \
            .set_query_id(lesson_id) \
            .set_result_resource_type(EducationalResourceType.root_knowledge) \
            .set_result_data_type(EducationalOntologySearchQuery.ResultDataType.id) \
            .exec()

        if len(root_ids) < 1:
            raise RuntimeError('找不到 root_knowledge_id!')

        return root_ids[0]

    def __init__(self, id, is_root_id=False):
        self._root_id = id if is_root_id else KnowledgeTree.get_root_id_by_lesson_id(id)
        self._lesson_id = None if is_root_id else id
        self._knowledge_nodes = {}
        self._knowledge_relationships = None

        self._refresh_knowledge_relationships()
        self._refresh_all_nodes()

    def _refresh_knowledge_relationships(self, lesson_id=None):
        if not lesson_id and not self._lesson_id:
            raise ValueError('刷新知识点关系时未传入 lesson_id！')
        elif not lesson_id:
            lesson_id = self._lesson_id
        else:
            self._lesson_id = lesson_id

        self._knowledge_relationships = KnowledgeRelationshipQuery(lesson_id).exec()

        return self

    def _refresh_all_nodes(self):
        self._refresh_from(self._root_id, is_root=True)

    def _refresh_from(self, knowledge_id, depth=1, is_root=False, parent_node=None):
        if depth == 1 and not is_root:
            raise ValueError("请设置 depth！")

        if is_root:
            depth = KnowledgeTree.root_depth
            knowledge_node = Node(knowledge_id, depth)
            self._root = knowledge_node
            self._knowledge_nodes[knowledge_id] = self._root
        else:
            knowledge_node = Node(knowledge_id, depth, parent_node)
            self._knowledge_nodes[knowledge_id] = knowledge_node

        if parent_node is not None:
            parent_node.add_child(knowledge_node)

        if knowledge_id not in self._knowledge_relationships:
            return

        if KnowledgeRelationship.hasChildNode not in self._knowledge_relationships[knowledge_id]:
            return

        children = self._knowledge_relationships[knowledge_id][KnowledgeRelationship.hasChildNode]
        for child_knowledge_id in children:
            self._refresh_from(child_knowledge_id, depth=depth+1, parent_node=knowledge_node)

    def get_root_id(self):
        return self._root_id

    def get_knowledge_node(self, knowledge_id):
        return self._knowledge_nodes[knowledge_id]

    def extend_knowledge(self, origin_knowledge_id, with_similarity):
        """
        返回一阶扩展后的知识点

        Args:
            origin_knowledge_id (str): 中心知识点 ID
            with_similarity (bool): 是否返回相似度

        Returns:
            不包含相似度：
                [{knowledge_id, relationships: [relationship, ...]}, ...]
            包含相似度：
                [{knowledge_id, relationships: [relationship, ...], similarity}, ...]
        """
        # eg. {relationship: [knowledge_id, ...], ...}
        knowledges_group_by_relationship = self._knowledge_relationships[origin_knowledge_id]

        # eg. {knowledge_id: {relationships: [relationship, ...]}, ...}
        result_group_by_knowledge_id = {}
        for relationship, knowledge_ids in knowledges_group_by_relationship.items():
            for knowledge_id in knowledge_ids:
                if "knowledge_id" not in result_group_by_knowledge_id:
                    result_group_by_knowledge_id[knowledge_id] = {}

                if "relationships" in result_group_by_knowledge_id[knowledge_id]:
                    result_group_by_knowledge_id[knowledge_id]["relationships"].append(relationship)
                else:
                    result_group_by_knowledge_id[knowledge_id]["relationships"] = [relationship]

        result = []
        for knowledge_id, item in result_group_by_knowledge_id.items():
            item_copy = item.copy()
            item_copy["knowledge_id"] = knowledge_id
            if with_similarity:
                item_copy["similarity"] = self.calculate_similarity(origin_knowledge_id, knowledge_id)
            result.append(item_copy)
        return result

    def get_relationships(self, origin_knowledge_id, target_knowledge_id):
        knowledges_group_by_relationship = self._knowledge_relationships[origin_knowledge_id]

        relationships = []
        for relationship, knowledge_ids in knowledges_group_by_relationship.items():
            if target_knowledge_id in knowledge_ids:
                relationships.append(relationship)

        return relationships

    def calculate_similarity(self, origin_knowledge_id, target_knowledge_id, options={}):
        def _distance():
            def _distance_of_same_depth(knowledge1, knowledge2):
                if knowledge1 == knowledge2:
                    return knowledge1.get_weight()

                return knowledge1.get_weight() + knowledge2.get_weight() + _distance_of_same_depth(knowledge1.get_parent(), knowledge2.get_parent())

            distance = 0
            if origin_knowledge.get_depth() > target_knowledge.get_depth():
                lower_node, higher_node = origin_knowledge, target_knowledge
            else:
                lower_node, higher_node = target_knowledge, origin_knowledge

            for depth in range(lower_node.get_depth(), higher_node.get_depth(), -1):
                distance += lower_node.get_weight()
                lower_node = lower_node.get_parent()
            distance += _distance_of_same_depth(lower_node, higher_node)
            return distance

        def _distance_similarity():
            def _adjusting_factor():
                return 2 * origin_knowledge.get_depth() / (origin_knowledge.get_depth() + target_knowledge.get_depth())

            factor = _adjusting_factor()
            return factor / (factor + _distance())

        def _relationship_similarity():
            def _calculate_similarity_by_relationships(relationships):
                weight_ordered_dict = OrderedDict([
                    (KnowledgeRelationship.hasSynonymNode, 1),
                    (KnowledgeRelationship.hasRelyOnNode, 0.8),
                    (KnowledgeRelationship.hasBeRelyByNode, 0.8),
                    (KnowledgeRelationship.hasParentNode, 0.7),
                    (KnowledgeRelationship.hasChildNode, 0.7),
                    (KnowledgeRelationship.hasRelateNode, 0.6),
                    (KnowledgeRelationship.hasBrotherNode, 0.5),
                    (KnowledgeRelationship.hasParallelNode, 0.2)
                ])

                weights = [weight_ordered_dict[relationship] for relationship in relationships]
                return max(weights) if len(weights) > 0 else 1

            relationships = self.get_relationships(origin_knowledge.get_id(), target_knowledge.get_id())

            return _calculate_similarity_by_relationships(relationships)

        origin_knowledge = self.get_knowledge_node(origin_knowledge_id)
        target_knowledge = self.get_knowledge_node(target_knowledge_id)

        alpha = options["alpha"] if "alpha" in options else 0.7
        beta = options["beta"] if "beta" in options else 1 - alpha

        return alpha * _distance_similarity() + beta * _relationship_similarity()
