from SPARQLWrapper import SPARQLWrapper, JSON
from retrieved.searchOperate import SearchOperate
from retrieved.knowledge_tree import KnowledgeTree
from retrieved.educational_ontology_search_query import EducationalOntologySearchQuery
from custom_types import EducationalResourceType

import time


class SearchResult:
    def __init__(self):
        self.sets = {type: set() for type in EducationalResourceType.getBasicTypes()}
        self.values = {type: [] for type in EducationalResourceType.getBasicTypes()}

    def merge(self, new_result):
        def _merge_related_search_resources(item, type):
            for resources in self.values[type]:
                if resources["id"] != item["id"]:
                    continue

                if "relatedSearchResources" not in resources:
                    resources["relatedSearchResources"] = item["relatedSearchResources"]
                    return

                for resource_type_key in item["relatedSearchResources"]:
                    if resource_type_key not in resources["relatedSearchResources"]:
                        resources["relatedSearchResources"][resource_type_key] = item["relatedSearchResources"][resource_type_key]
                        continue

                    resources["relatedSearchResources"][resource_type_key] \
                        = list(set(resources["relatedSearchResources"][resource_type_key] + item["relatedSearchResources"][resource_type_key]))

        """ 添加 new_result 中对应的且未搜索到的资源 """
        if isinstance(new_result, SearchResult):
            new_result = new_result.values

        for type in self.values:
            for item in new_result[type]:
                if item["id"] not in self.sets[type]:
                    self.add(type, item)
                elif "relatedSearchResources" in item:
                    _merge_related_search_resources(item, type)

        return self

    def to_json(self):
        return {enum_key.value + "s": item for enum_key, item in self.values.items()}

    def _get_from_specified_type(self, resource_id, resource_type):
        if resource_id in self.sets[resource_type]:
            for item in self.values[resource_type]:
                if resource_id == item["id"]:
                    return item
        return None

    def get(self, resource_id=None, resource_type=None):
        search_all_type_of_resources = True if resource_type is None else False
        return_all_resource_under_the_type = True if resource_id is None else False

        if search_all_type_of_resources and return_all_resource_under_the_type:
            return self.values

        if not search_all_type_of_resources and not return_all_resource_under_the_type:
            resource = self._get_from_specified_type(resource_id, resource_type)
            if resource is not None:
                return resource

        if search_all_type_of_resources:
            for type in self.sets:
                resource = self._get_from_specified_type(resource_id, type)
                if resource is not None:
                    return resource

        if return_all_resource_under_the_type:
            return self.values[resource_type]

        return None

    def has(self, resource_id, resource_type=None):
        search_all_resources = True if resource_type is None else False

        if search_all_resources:
            for type in self.sets:
                if resource_id in self.sets[type]:
                    return True
        else:
            if resource_id in self.sets[resource_type]:
                return True

        return False

    def batch_add(self, resource_type, resources):
        for resource in resources:
            self.add(resource_type, resource)
        return self

    def add(self, resource_type, resource):
        if not resource["id"]:
            raise RuntimeError("Unsupported resource: {}", resource)

        self.values[resource_type].append(resource)
        self.sets[resource_type].add(resource["id"])
        return self


class SearchManagerV2:
    def __init__(self):
        pass

    def search(self, keyword, options, cached_resources=SearchResult()):
        """
        根据关键字进行检索，返回对应类型的检索资源

        Args:
            keyword (str): 检索关键字
            options (dict): 选项，包括
                resource_types: 代表资源类型数组，可以包含含 "knowledge", "kunit", "mcourse", "acourse", "lesson" 在内的各类资源
            cached_resources (SearchResult): 已缓存的资源，可直接使用 .get(id, resource_type) 获取对应资源

        Returns:
            SearchResult
        """
        search_result = SearchResult()
        resource_types = options["resource_types"]

        for type in resource_types:
            search_result.merge(self._search_specific_type(keyword, type, cached_resources))

        return search_result

    def get_lessons_by_resources(self, resource_type, resource_ids):
        result = SearchResult()
        lessons = EducationalOntologySearchQuery() \
            .set_query_resource_type(resource_type) \
            .set_query_ids(resource_ids) \
            .set_result_resource_type(EducationalResourceType.lesson) \
            .set_result_data_type(EducationalOntologySearchQuery.ResultDataType.info) \
            .set_with_related_search_resources() \
            .exec()

        return result.batch_add(EducationalResourceType.lesson, lessons)

    def _search_specific_type(self, keyword, type, cached_resources):
        def search_functions(type):
            if type == EducationalResourceType.knowledge:
                return self._search_knowledge

            return lambda k, cr: self._search_simple_properties(k, type, cr)

        if type in EducationalResourceType:
            return search_functions(type)(keyword, cached_resources)
        else:
            raise RuntimeError("Unsupported resource type {}!".format(type))

    def _search_simple_properties(self, keyword, type, cached_resources):
        search_result = SearchResult()

        ids = set(EducationalOntologySearchQuery()
                  .set_query_resource_type(type)
                  .set_query_keyword(keyword)
                  .set_result_resource_type(type)
                  .set_result_data_type(EducationalOntologySearchQuery.ResultDataType.id)
                  .exec())

        uncached_ids = set()
        for id in ids:
            if cached_resources.has(id, type):
                search_result.add(type, cached_resources.get(id, type))
            else:
                uncached_ids.add(id)

        if len(uncached_ids) > 0:
            uncached_resources = EducationalOntologySearchQuery() \
                .set_query_resource_type(type) \
                .set_query_ids(uncached_ids) \
                .set_result_resource_type(type) \
                .set_result_data_type(EducationalOntologySearchQuery.ResultDataType.info) \
                .exec()
            search_result.batch_add(type, uncached_resources)

        return search_result

    def _search_knowledge(self, keyword, cached_resources):
        def _remove_duplicate(dict_list, key, keep_first):
            result_dict = {}
            for item in dict_list:
                if not(item[key] in result_dict and keep_first(result_dict[key], item)):
                    result_dict[key] = item

            return [item for _, item in result_dict.items()]

        CALCULATE_TIME = True
        if CALCULATE_TIME:
            start_time = time.clock()

        search_result = self._search_simple_properties(keyword, EducationalResourceType.knowledge, cached_resources)

        if CALCULATE_TIME:
            after_simple_search = time.clock()

        knowledges = search_result.get(resource_type=EducationalResourceType.knowledge)
        knowledge_similaritys = {}
        extended_knowledges_with_similarity = []
        knowledge_trees = {}

        for knowledge in knowledges:
            lesson_ids = EducationalOntologySearchQuery() \
                .set_query_resource_type(EducationalResourceType.knowledge) \
                .set_query_id(knowledge["id"]) \
                .set_result_resource_type(EducationalResourceType.lesson) \
                .set_result_data_type(EducationalOntologySearchQuery.ResultDataType.id) \
                .exec()

            if len(lesson_ids) <= 0:
                continue
            lesson_id = lesson_ids[0]

            if lesson_id in knowledge_trees:
                knowledge_tree = knowledge_trees[lesson_id]
            else:
                knowledge_tree = KnowledgeTree(lesson_id)
                knowledge_trees[lesson_id] = knowledge_tree

            # eg. [{ 'knowledge_id': 'xxx', 'similarity': 1 }, ...]
            extended_knowledges_with_similarity.append({"knowledge_id": knowledge["id"], "similarity": 1})
            extended_knowledges_with_similarity += knowledge_tree.extend_knowledge(knowledge["id"], with_similarity=True)
            _remove_duplicate(extended_knowledges_with_similarity, "knowledge_id", lambda x, y: x["similarity"] > y["similarity"])

        if CALCULATE_TIME:
            after_extend = time.clock()

        knowledge_ids = set()
        for item in extended_knowledges_with_similarity:
            knowledge_id = item["knowledge_id"]
            knowledge_ids.add(knowledge_id)

            have_stored = knowledge_id in knowledge_similaritys
            if (have_stored and knowledge_similaritys[knowledge_id] < item["similarity"]) \
                    or (not have_stored):
                knowledge_similaritys[knowledge_id] = item["similarity"]

        knowledges = EducationalOntologySearchQuery() \
            .set_query_resource_type(EducationalResourceType.knowledge) \
            .set_query_ids(knowledge_ids) \
            .set_result_resource_type(EducationalResourceType.knowledge) \
            .set_result_data_type(EducationalOntologySearchQuery.ResultDataType.info) \
            .exec()

        if CALCULATE_TIME:
            after_research = time.clock()

        for knowledge in knowledges:
            knowledge["similarity"] = knowledge_similaritys[knowledge["id"]]

        if CALCULATE_TIME:
            print("""
            首次搜索知识点耗时：{:.2f}s，扩展并计算相关度耗时：{:.2f}s，重新进行搜索耗时：{:.2f}s
            """.format(after_simple_search - start_time,
                       after_extend - after_simple_search,
                       after_research - after_extend))

        return SearchResult().batch_add(EducationalResourceType.knowledge, knowledges)

