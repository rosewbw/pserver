from SPARQLWrapper import SPARQLWrapper, JSON, POST
from retrieved.tree import Node


class SearchOperate:
    # SearchOperate 用于语义相似度的计算
    def __init__(self, kg_name, root_knowledge_id):
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
        self.root = None
        self.kg_name = kg_name
        self.get_kg_from_server(root_knowledge_id)

    def get_kg_from_server(self, root_knowledge_id):
        root = Node(root_knowledge_id, 1)
        self.root = root
        self.get_kg_info(root, root_knowledge_id)

    def get_root(self):
        return self.root

    def get_kg_info(self, parent_node, node_id):
        results = self.search_node(node_id, 'hasChildNode')
        if results:
            # parent_node.update_width(len(results))
            for result in results:
                node = Node(result["knowledge_id"], parent_node.get_depth() + 1, parent_node)
                parent_node.add_child(node)
                self.get_kg_info(node, result["knowledge_id"])
        return parent_node

    def search_node(self, node, search_type):
        sqlstr_SELECT = """
                SELECT ?knowledge_id
                """
        sqlstr_WHERE = """
                WHERE {
                    knowledge:%s basic:%s ?knowledge_id.
                }
                """ % (node, search_type)
        result = self.search_request(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
        return result

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

    def get_tree_node(self, node_value):
        result = self.search_tree_node(self.get_root(), node_value)
        return result

    def search_tree_node(self, tree, node_value):
        result = None
        if tree.get_value() == node_value:
            return tree
        children = tree.get_child_list()
        if len(children) != 0:
            for child in children:
                if child.get_value() == node_value:
                    return child
                result = self.search_tree_node(child, node_value)
                if result is None:
                    continue
                else:
                    return result

    def calculate_distance(self, node1, node2):
        if node1.get_value() == node2.get_value():
            return 0
        else:
            n1 = node1
            n2 = node2
            distance = 0
            dis1 = n1.get_weight()
            dis2 = n2.get_weight()
            flag = True
            while flag:
                if n1.get_value() == n2.get_value():
                    distance += dis1 + dis2 - n1.get_weight()
                    flag = False
                else:
                    if not n2.get_parent() is None:
                        n2 = n2.get_parent()
                        dis2 += n2.get_weight()
                    else:
                        if not n1.get_parent() is None:
                            n1 = n1.get_parent()
                            n2 = node2
                            dis2 = n2.get_weight()
                            dis1 += n1.get_weight()
                        else:
                            distance = 0
                            flag = False
        return distance

    def get_distance(self, node1, node2):
        node1_parents = {}
        node2_parents = {}
        self.get_all_parent_nodes(node1_parents, node1)
        self.get_all_parent_nodes(node2_parents, node2)
        distance = 0
        n1 = node1_parents
        n2 = node2_parents
        flag = True
        while flag:
            if n1["key"] == n2["key"]:
                distance = n1["height"] + n2["height"]
                flag = False
            else:
                if n2["parentNode"] != {}:
                    n2 = n2["parentNode"]
                else:
                    if n1["parentNode"] != {}:
                        n1 = n1["parentNode"]
                        n2 = node2_parents
                    else:
                        flag = False
        return distance

    def get_all_parent_nodes(self, nodes, node, height=0):
        nodes.setdefault("key", node)
        nodes.setdefault("height", height)
        results = self.search_node(node, 'hasParentNode')
        if results:
            nodes.setdefault("parentNode", {})
            height += 1
            for result in results:
                self.get_all_parent_nodes(nodes["parentNode"], result, height=height)
        else:
            nodes.setdefault("parentNode", {})
            return
        return nodes

    def calculate_sim_distance(self, node1, node2):
        distance = self.calculate_distance(node1, node2)
        alpha = 2 * node1.get_depth() / (node1.get_depth() + node2.get_depth())
        # alpha = pow(0.5, node1.get_depth())
        # alpha = 0.5
        sim_distance = alpha / (alpha + distance)
        return sim_distance

    def calculate_sim_relativity(self, node1, node2):
        result = self.search_node(node1.get_value(), "hasRelateNode")
        sim_relativity = 0
        return sim_relativity

    def calculate_sim(self, node1, extend_ndoes):
        result = []
        result.append({
            'knowledge_id': node1.get_value(),
            'similarity': 1
        })
        for node in extend_ndoes:
            children = extend_ndoes[node]["child"]
            if len(children) == 0:
                continue
            else:
                if node == "brother" or node == "synonym":
                    for child in children:
                        if node1.get_value() == child["knowledge_id"]:
                            continue
                        else:
                            temp = {}
                            temp.setdefault("n1", node1.get_value())
                            temp.setdefault("n2", child["knowledge_id"])
                            n2 = self.get_tree_node(child["knowledge_id"])
                            sim = self.calculate_sim_distance(node1, n2) * 0.7 + 0.5 * 0.3
                            if sim >= 0.8:
                                temp.setdefault("sim", sim)
                                result.append(temp)
                else:
                    if node == "child":
                        self.calculate_sim_func(result, node1, children, 0.7)
                    if node == "parent":
                        self.calculate_sim_func(result, node1, children, 0.7)
                    if node == "relyon" or node == "berelyon":
                        self.calculate_sim_func(result, node1, children, 0.8)
                    if node == "related":
                        self.calculate_sim_func(result, node1, children, 0.6)
        return result

    def calculate_sim_func(self, result, node1, nodes, degree):
        for child in nodes:
            temp = {}
            temp.setdefault("knowledge_id", child["value"])
            n2 = self.get_tree_node(child["value"])
            sim = self.calculate_sim_distance(node1, n2) * 0.7 + pow(degree, child["depth"]) * 0.3
            if sim >= 0.8:
                temp.setdefault("similarity", sim)
                result.append(temp)
            if len(child) == 3:
                self.calculate_sim_func(result, node1, child["child"], degree)
        return

    def search_related_nodes(self, node1, node2):
        result = 0
        return result

    def get_all_node(self):
        result = []
        root = self.root
        self.get_all_node_func(root, result)
        return result

    def get_all_node_func(self, node, result):
        result.append(node)
        children = node.get_child_list()
        if len(children) != 0:
            for child in children:
                self.get_all_node_func(child, result)
        else:
            return

    def extend_node(self, node):
        if node is None:
            return
        else:
            result = {}
            result.setdefault("synonym", self.extend_synonym_node(node))
            result.setdefault("brother", self.extend_brother_node(node))
            result.setdefault("related", self.extend_related_node(node))
            result.setdefault("parallel", self.extend_parallel_node(node))
            result.setdefault("relyon", self.extend_rely_node(node))
            result.setdefault("berelyon", self.extend_be_rely_node(node))
            result.setdefault("parent", self.extend_parent_node(node))
            result.setdefault("child", self.extend_child_node(node))
        return result

    def extend_synonym_node(self, node):
        result = {}
        results = []
        for item in self.search_node(node.get_value(), "hasSynonymNode"):
            results.append(item)
        result.setdefault("value", node.get_value())
        result.setdefault("child", results)
        return result

    def extend_brother_node(self, node):
        result = {}
        results = []
        for item in self.search_node(node.get_value(), "hasBrotherNode"):
            results.append(item)
        result.setdefault("value", node.get_value())
        result.setdefault("child", results)
        return result

    def extend_be_rely_node(self, node):
        result = {}
        self.extend_be_rely_node_func(result, node.get_value(), 0)
        return result

    def extend_be_rely_node_func(self, nodes, node_value, depth):
        nodes.setdefault("value", node_value)
        nodes.setdefault("depth", depth)
        nodes.setdefault("child", [])
        results = self.search_node(node_value, "hasBeRelyByNode")
        if results:
            depth += 1
            for result in results:
                temp = {}
                nodes["child"].append(temp)
                self.extend_be_rely_node_func(temp, result["knowledge_id"], depth)
        return

    def extend_parallel_node(self, node):
        result = {}
        self.extend_parallel_node_func(result, node.get_value(), 0, node.get_value())
        return result

    def extend_parallel_node_func(self, nodes, node_value, depth, origin_node):
        nodes.setdefault("value", node_value)
        nodes.setdefault("depth", depth)
        nodes.setdefault("child", [])
        results = self.search_node(node_value, "hasParentNode")
        if results:
            depth += 1
            for result in results:
                if origin_node == result:
                    if len(results) == 1:
                        return
                    else:
                        continue
                else:
                    temp = {}
                    nodes["child"].append(temp)
                    self.extend_parallel_node_func(temp, result["knowledge_id"], depth, origin_node)
        return

    def extend_rely_node(self, node):
        result = {}
        self.extend_rely_node_func(result, node.get_value(), 0)
        return result

    def extend_rely_node_func(self, nodes, node_value, depth):
        nodes.setdefault("value", node_value)
        nodes.setdefault("depth", depth)
        nodes.setdefault("child", [])
        results = self.search_node(node_value, "hasRelyOnNode")
        if results:
            depth += 1
            for result in results:
                temp = {}
                nodes["child"].append(temp)
                self.extend_rely_node_func(temp, result["knowledge_id"], depth)
        return

    def extend_child_node(self, node):
        result = {}
        self.extend_child_node_func(result, node.get_value(), 0)
        return result

    def extend_child_node_func(self, nodes, node_value, depth):
        nodes.setdefault("value", node_value)
        nodes.setdefault("depth", depth)
        nodes.setdefault("child", [])
        results = self.search_node(node_value, "hasChildNode")
        if results:
            depth += 1
            for result in results:
                temp = {}
                nodes["child"].append(temp)
                self.extend_child_node_func(temp, result["knowledge_id"], depth)
        return

    def extend_parent_node(self, node):
        result = {}
        self.extend_parent_node_func(result, node.get_value(), 0)
        return result

    def extend_parent_node_func(self, nodes, node_value, depth):
        nodes.setdefault("value", node_value)
        nodes.setdefault("depth", depth)
        nodes.setdefault("child", [])
        results = self.search_node(node_value, "hasParentNode")
        if results:
            depth += 1
            for result in results:
                temp = {}
                nodes["child"].append(temp)
                self.extend_parent_node_func(temp, result["knowledge_id"], depth)
        return

    def extend_related_node(self, node):
        result = {}
        collection = []
        collection.append(node.get_value())
        self.extend_related_node_func(result, node.get_value(), 0, collection)
        return result

    def extend_related_node_func(self, nodes, node_value, depth, collection):
        nodes.setdefault("value", node_value)
        nodes.setdefault("depth", depth)
        nodes.setdefault("child", [])
        results = self.search_node(node_value, "hasRelateNode")
        if results:
            for result in results:
                if result in collection:
                    if len(results) == 1:
                        return
                    else:
                        continue
                else:
                    depth += 1
                    temp = {}
                    nodes["child"].append(temp)
                    collection.append(result)
                    self.extend_related_node_func(temp, result["knowledge_id"], depth, collection)
        return

    def get_result(self, knowledge_id):
        knowledge_node = self.get_tree_node(knowledge_id)
        knowledge_extend_node = self.extend_node(knowledge_node)
        all_collection = self.calculate_sim(knowledge_node, knowledge_extend_node)
        # 结果排序
        sorted_collection = sorted(all_collection, key=lambda c: c['similarity'], reverse=True)
        # 结果去重
        result = self._remove_duplicate(sorted_collection)
        return result

    def _remove_duplicate(self, dict_list):
        seen = set()
        new_dict_list = []
        for dict in dict_list:
            t_dict = {'knowledge_id': dict['knowledge_id']}
            t_tup = tuple(t_dict.items())
            if t_tup not in seen:
                seen.add(t_tup)
                new_dict_list.append(dict)
        return new_dict_list


