from enum import Enum


class EducationalResourceType(Enum):
    lesson = "lesson"
    knowledge = "knowledge"
    kunit = "kunit"
    mcourse = "mcourse"
    acourse = "acourse"

    root_knowledge = "rootKnowledge"

    @classmethod
    def getBasicTypes(cls):
        return [
            cls.lesson,
            cls.knowledge,
            cls.kunit,
            cls.mcourse,
            cls.acourse,
        ]

    @classmethod
    def isBasicType(cls, type):
        return type in cls.getBasicTypes()


class KnowledgeRelationship(Enum):
    hasChildNode = "basic:hasChildNode"
    hasParentNode = "basic:hasParentNode"
    hasParallelNode = "basic:hasParallelNode"
    hasBrotherNode = "basic:hasBrotherNode"
    hasRelyOnNode = "basic:hasRelyOnNode"
    hasBeRelyByNode = "basic:hasBeRelyByNode"
    hasNextNode = "basic:hasNextNode"
    hasPrevNode = "basic:hasPrevNode"
    hasSynonymNode = "basic:hasSynonymNode"
    hasRelateNode = "basic:hasRelateNode"

    @classmethod
    def parse(cls, string):
        if string.find(":") == -1:
            string = "basic:{}".format(string)

        return cls(string)


