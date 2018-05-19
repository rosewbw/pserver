#
#
# def get_extend_nodes(self, nodes, node):
#     nodes.append(node)
#     child_nodes = []
#     self.get_child_nodes(child_nodes, node, 3, 0)
#     nodes += child_nodes
#
#     related_node = []
#     self.get_related_nodes(related_node, node)
#     nodes += related_node
#
#     parent_node = self.get_parent_node(node)
#     nodes += parent_node
#
#     brother_node = []
#     self.get_brother_nodes(brother_node, node)
#     nodes += brother_node
#
#     parallel_node = []
#     self.get_parallel_nodes(parallel_node, node)
#     nodes += parallel_node
#
#     return nodes
#
#
# def get_child_nodes(self, nodes, node, depth_limit, depth=0):
#     if depth != 0:
#         nodes.append(node)
#     results = self.search_node(node, 'hasChildNode')
#     if results:
#         depth += 1
#         if depth < depth_limit:
#             for result in results:
#                 self.get_child_nodes(nodes, result, depth_limit, depth=depth)
#     return nodes
#
#
# def get_related_nodes(self, nodes, node):
#     results = self.search_node(node, 'isRelatedTo')
#     nodes += results
#     return nodes
#
#
# # 查询父节点
# def get_parent_node(self, node):
#     parent_node = ''
#     results = self.search_node(node, 'hasParentNode')
#     for result in results:
#         parent_node = result
#     return parent_node
#
#
# def get_brother_nodes(self, nodes, node):
#     results = self.search_node(node, 'hasBrotherNode')
#     nodes += results
#     return
#
#
# def get_parallel_nodes(self, nodes, node):
#     results = self.search_node(node, 'hasBrotherNode')
#     nodes += results
#     return
#
#
# def search_node(self, node, search_type):
#     sqlstr_SELECT = """
#             SELECT ?s
#             """
#     sqlstr_WHERE = """
#             WHERE {
#                 :%s :%s ?s.
#             }
#             """ % (node, search_type)
#
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     results = self.sparql.query().convert()  # 通过HTTP向SPARQL终端"http://localhost:3030/mathdb/query"发起
#
#     # 查询请求，通过JSON格式接受返回的数据，存入results中
#     subClass = []
#     for result in results["results"]["bindings"]:
#         subClass.append(result["s"]["value"].split("#")[-1])
#     return subClass
#
#
# def get_all_parent_nodes(self, nodes, node, height=0):
#     nodes.setdefault("key", node)
#     nodes.setdefault("height", height)
#     results = self.search_node(node, 'hasParentNode')
#     if results:
#         nodes.setdefault("parentNode", {})
#         height += 1
#         for result in results:
#             self.get_all_parent_nodes(nodes["parentNode"], result, height=height)
#     else:
#         nodes.setdefault("parentNode", {})
#         return
#     return nodes
#
#
# def get_distance(self, node1, node2):
#     node1_parents = {}
#     node2_parents = {}
#     self.get_all_parent_nodes(node1_parents, node1)
#     self.get_all_parent_nodes(node2_parents, node2)
#     distance = 0
#     n1 = node1_parents
#     n2 = node2_parents
#     flag = True
#     while flag:
#         if n1["key"] == n2["key"]:
#             distance = n1["height"] + n2["height"]
#             flag = False
#         else:
#             if n2["parentNode"] != {}:
#                 n2 = n2["parentNode"]
#             else:
#                 if n1["parentNode"] != {}:
#                     n1 = n1["parentNode"]
#                     n2 = node2_parents
#                 else:
#                     flag = False
#     return distance
#
#
# def get_node_depth(self, node):
#     depth = 0
#     parent_node = node
#     while self.get_parent_node(parent_node) != '':
#         depth += 1
#         parent_node = self.get_parent_node(parent_node)
#     return depth
#
#
# # 获取共同父节点
# def get_common_node(self, node1, node2):
#     node1_parents = {}
#     node2_parents = {}
#     self.get_all_parent_nodes(node1_parents, node1)
#     self.get_all_parent_nodes(node2_parents, node2)
#     n1 = node1_parents["parentNode"]
#     n2 = node2_parents["parentNode"]
#     node = ''
#     flag = True
#     while flag:
#         if n1["key"] == n2["key"]:
#             node = n1["key"]
#             flag = False
#         else:
#             if n2["parentNode"] != {}:
#                 n2 = n2["parentNode"]
#             else:
#                 if n1["parentNode"] != {}:
#                     n1 = n1["parentNode"]
#                     n2 = node2_parents
#                 else:
#                     flag = False
#     return node
#
#
# # 获取节点的度
# def get_common_degree(self, node):
#     results = self.search_node(node, 'hasChildNode')
#     degree = len(results)
#     print(node, degree)
#     return degree
#
#
# # 获取树的度
# def get_tree_degree(self, node, degree=0):
#     results = self.search_node(node, 'hasChildNode')
#     if results:
#         for result in results:
#             node_degree = self.get_common_degree(result)
#             if degree < node_degree:
#                 degree = node_degree
#             self.get_tree_degree(result, degree)
#     return degree
#
#
# # 获取根节点
# def get_root_node(self, node):
#     root = self.get_parent_node(node)
#     while self.get_parent_node(root) != '':
#         root = self.get_parent_node(root)
#     return root
#
#
# def calculate_sim_distance(self, node1, node2):
#     distance = self.get_distance(node1, node2)
#     sim_distance = 1 / (1 + distance * distance)
#     return sim_distance
#
#
# def calculate_sim_width(self, node1, node2):
#     common_degree = self.get_common_degree(self.get_common_node(node1, node2))
#     tree_degree = self.get_tree_degree(self.get_root_node(node1))
#     sim_width = common_degree / tree_degree
#     return sim_width
#
#
# #
# def calculate_sim_depth(self, node1, node2):
#     depth1 = self.get_node_depth(node1)
#     depth2 = self.get_node_depth(node2)
#     sim_depth = 1 - (2 * abs(depth1 - depth2)) / (depth2 + depth1)
#     return sim_depth
#
#
# def calculate_sim(self, node1, node2):
#     sim_distance = self.calculate_sim_distance(node1, node2)
#     sim_width = self.calculate_sim_width(node1, node2)
#     sim_depth = self.calculate_sim_depth(node1, node2)
#     sim = 0.7 * sim_distance + 0.2 * sim_width + 0.1 * sim_depth
#     return sim


# # search request
# def search_property_range(self, property_name):
#     sqlstr_SELECT = """
#     SELECT ?range
#     """
#     sqlstr_WHERE = """
#     WHERE{
#         course:%s rdfs:range ?range
#     }
#     """ % property_name
#
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     results = self.sparql.query().convert()
#     result = re.search(r'string', results['results']['bindings'][0]['range']['value'])
#     if result:
#         return 'string'
#     else:
#         result = re.search(r'float', results['results']['bindings'][0]['range']['value'])
#         if result:
#             return 'float'
#         else:
#             return 'int'
#
# # create request
# def create_individual(self, class_type, individual_id, options):
#     if individual_id:
#         insert_str_subject = """course:%s """ % individual_id
#         insert_str = insert_str_subject + "rdf:type owl:NameIndividual.\n "
#         insert_str += insert_str_subject + """rdf:type course:%s.\n""" % class_type
#         for key in options:
#             range_type = self.search_property_range(key)
#             if range_type == 'string':
#                 insert_str += insert_str_subject + """course:%s \"%s\".\n""" % (key, options[key])
#             elif range_type == 'float':
#                 insert_str += insert_str_subject + """course:%s %.2f.\n""" % (key, options[key])
#             else:
#                 insert_str += insert_str_subject + """course:%s %i.\n""" % (key, options[key])
#     else:
#         return ''
#     sqlstr_INSERT = "INSERT DATA{\n" + insert_str + "}"
#     self.sparql.setMethod(POST)
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)
#     result = self.sparql.query().convert().decode("utf-8")
#
#     return result
#
# def associate_knowledge(self, first_knowledge_id, second_knowledge_id, relation_type):
#     sqlstr_INSERT = """
#     INSERT DATA{
#         course:%s course:%s course:%s.
#     }
#     """ % (first_knowledge_id, relation_type, second_knowledge_id)
#
#     self.sparql.setMethod(POST)
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)
#     result = self.sparql.query().convert().decode("utf-8")
#     if "Success" in result:
#         return True
#     else:
#         return False
#
# def bind_teaching_unit(self, knowledge_id, teaching_unit_id):
#     sqlstr_SELECT = """
#     SELECT ?tunit
#     """
#     sqlstr_WHERE = """
#     WHERE{
#     course:%s course:has教学单元 ?tunit.
#     }
#     """ % knowledge_id
#
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     results = self.sparql.query().convert()
#     if results['results']['bindings']:
#         return '该知识点下已经存在教学单元'
#
#     sqlstr_INSERT = """
#     INSERT DATA{
#     course:%s course:has教学单元 course:%s.
#     }
#     """ % (knowledge_id, teaching_unit_id)
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     result = self.sparql.query().convert().decode("utf-8")
#     if 'Success' in result:
#         return True
#     else:
#         return False
#
# def bind_mainlesson_to_unit(self, teaching_unit_id, mainlesson_id):
#     sqlstr_SELECT = """
#     SELECT ?mlesson
#     """
#     sqlstr_WHERE = """
#     WHERE{
#     course:%s course:has课时 ?lesson.
#     ?lesson course:课时类型 ?mlesson.
#     FILTER (?mlesson = \"%s\")
#     }
#     """ % (teaching_unit_id, '主课时')
#
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     results = self.sparql.query().convert()
#     if results['results']['bindings']:
#         return "已经存在主课时"
#
#     sqlstr_INSERT = """
#     INSERT DATA{
#     course:%s has课时 course:%s
#     }
#     """ % (teaching_unit_id, mainlesson_id)
#
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     result = self.sparql.query().convert().decode("utf-8")
#     if 'Success' in result:
#         return True
#     else:
#         return False
#
# def bind_auxlesson_to_unit(self, teaching_unit_id, auxlesson_id):
#     sqlstr_INSERT = """
#     INSERT DATA{
#     course:%s has课时 course:%s
#     }
#     """ % (teaching_unit_id, auxlesson_id)
#
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     result = self.sparql.query().convert().decode("utf-8")
#     if 'Success' in result:
#         return True
#     else:
#         return False
#
# def add_learning_property(self, student_id, target_id):
#     sqlstr_INSERT = """
#     course:%s course:正在学习 course:%s
#     """ % (student_id, target_id)
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     result = self.sparql.query().convert().decode("utf-8")
#     if 'Success' in result:
#         return True
#     else:
#         return False
#
# def delete_learning_property(self, student_id, target_id):
#     sqlstr_DELETE = """
#     DELETE{
#     course:%s course:正在学习 course:%s
#     }
#     """ % (student_id, target_id)
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_DELETE)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     result = self.sparql.query().convert().decode("utf-8")
#     if 'Success' in result:
#         return True
#     else:
#         return False
#
# def add_student_to_teacher(self, student_id, teacher_id):
#     # sqlstr_SELECT = """
#     # SELECT ?student
#     # """
#     # sqlstr_WHERE = """
#     # WHERE{
#     # course:%s course:has学生 ?student
#     # }
#     # """
#     # self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_SELECT + sqlstr_WHERE)  # 这一步编辑查询语句
#     # self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     # results = self.sparql.query().convert()
#     # if results['results']['bindings']:
#     #     return "已经存在主课时"
#     sqlstr_INSERT = """
#     INSERT DATA{
#     course:%s course:has学生 course:%s.
#     }
#     """ % (teacher_id, student_id)
#     self.sparql.setQuery(self.sqlstr_PREFIX + sqlstr_INSERT)  # 这一步编辑查询语句
#     self.sparql.setReturnFormat(JSON)  # 规定查询结果的表现形式
#     result = self.sparql.query().convert().decode("utf-8")
#     if 'Success' in result:
#         return True
#     else:
#         return False