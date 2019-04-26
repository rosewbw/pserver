class Node:
    def __init__(self, value, depth, parent=None):
        self.value = value
        self.depth = depth
        self.width = 0
        self.child_list = []
        self.parent = parent
        self.weight = 1
        # self._update_child_weight()

    def add_child(self, node):
        self.child_list.append(node)
        self.width += 1
        self.update_weight()
        self.update_child_weight()

    def remove_child(self, node):
        self.width -= 1
        self.child_list.remove(node)

        self.update_weight()
        self.update_child_weight()

    def get_value(self):
        return self.value

    def get_parent(self):
        return self.parent

    def get_depth(self):
        return self.depth

    def get_child_list(self):
        return self.child_list

    def get_weight(self):
        return self.weight

    def set_value(self, value):
        self.value = value

    def set_depth(self, depth):
        self.depth = depth
        self.update_child_weight()

    def update_weight(self):
        if self.parent:
            self.weight = self.parent.get_weight() / (self.depth + self.width)
        else:
            self.weight = 1

    def update_child_weight(self):
        children = self.child_list
        for child in children:
            child._update_weight()
