from learningPath.KnowledgeTracingModel import KnowledgeTracingModel
from learningPath.KnowledgeRecommendationModel import KnowledgeRecommendationModel

SUPPORTED_COURSES = ['ASSISTment2009-2010']


class LearningPathSponsor:
    def __init__(self):
        self.knowledge_tracing_models = {}
        self.knowledge_recommendation_models = {}

    def _init_knowledge_tracing_model(self, course_name):
        self.knowledge_tracing_models[course_name] = KnowledgeTracingModel(course_name)

    def _init_knowledge_recommendation_model(self, course_name):
        self.knowledge_recommendation_models[course_name] = KnowledgeRecommendationModel(course_name)

    def _init_model(self, course_name):
        self._init_knowledge_tracing_model(course_name)
        self._init_knowledge_recommendation_model(course_name)

    def recommend(self, course, learning_history):
        if course not in SUPPORTED_COURSES:
            raise RuntimeError('Unsupported course: {}'.format(course))

        if (course not in self.knowledge_tracing_models) or (course not in self.knowledge_recommendation_models):
            self._init_model(course)

        knowledge_levels = self.knowledge_tracing_models[course].predict_knowledge_levels(learning_history)
        len_knowledge_levels = len(knowledge_levels)
        if len_knowledge_levels < 20:
            consecutive_states = [knowledge_levels[0] for _ in range(20)]
            consecutive_states[-len_knowledge_levels:] = knowledge_levels
        else:
            consecutive_states = knowledge_levels[-20:]
        recommend_knowledge = self.knowledge_recommendation_models[course].recommend(consecutive_states)

        return int(recommend_knowledge)
