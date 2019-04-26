class KnowledgeNode:
    def __init__(self, value, depth, parent=None):
        self._value = value
        self._depth = depth
        self._width = 0
        self._child_list = []
        self._parent = parent
        self._weight = 1
        # self._update_child_weight()

    def add_child(self, node):
        self._child_list.append(node)
        self._width += 1

        # TODO: 这里要循环更新 weight 是否可优化
        self._update_weight()
        self._update_child_weight()

        return self

    def remove_child(self, node):
        self._width -= 1
        self._child_list.remove(node)

        # TODO: 这里要循环更新 weight 是否可优化
        self._update_weight()
        self._update_child_weight()

        return self

    def get_value(self):
        return self._value

    def get_id(self):
        return self._value

    def get_parent(self):
        return self._parent

    def get_depth(self):
        return self._depth

    def get_child_list(self):
        return self._child_list

    def get_weight(self):
        return self._weight

    def set_value(self, value):
        self._value = value

    def set_depth(self, depth):
        self._depth = depth
        self._update_child_weight()

    def _update_weight(self):
        if self._parent:
            self._weight = self._parent.get_weight() / (self._depth + self._width)
        else:
            self._weight = 1

    def _update_child_weight(self):
        for child in self._child_list:
            child._update_weight()
