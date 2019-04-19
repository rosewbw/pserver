import os
import tensorflow as tf

from learningPath.utils.load_data import OriginalInputProcessor
from learningPath.utils.utils import DKT


file_path, _ = os.path.split(os.path.realpath(__file__))
input_processor = OriginalInputProcessor()

MODEL_CONFIG = {
    'ASSISTment2009-2010': {
        'model_path': os.path.join(file_path, './model/LSTM-200'),
        'num_skills': 111,
    }
}


class KnowledgeTracingModel:
    def __init__(self, course_name):
        if course_name not in MODEL_CONFIG:
            raise RuntimeError('不存在对应 model')

        self.model_path = MODEL_CONFIG[course_name]["model_path"]
        self.num_skills = MODEL_CONFIG[course_name]["num_skills"]

        self.graph = tf.Graph()
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        self.sess = tf.Session(config=config, graph=self.graph)

        network_config = {
            'batch_size': 32,
            'hidden_layer_structure': [200,],
            'learning_rate': 1e-2,
            'keep_prob': 0.333,
            'rnn_cell': tf.contrib.rnn.LSTMCell,
            'lambda_w1': 0.003,
            'lambda_w2': 3.0,
            'lambda_o': 0.1
        }
        with self.graph.as_default():
            self.model = DKT(self.sess, None, None, self.num_skills, network_config, logging=False)
            self.model.model.build_graph()
            self.model.load_model(self.model_path)

    def predict_knowledge_levels(self, learning_history):
        problem_seqs = [[problem for (problem, correct) in learning_history]]
        correct_seqs = [[correct for (problem, correct) in learning_history]]
        model_input, _, _ = input_processor.process_problems_and_corrects(problem_seqs, correct_seqs, self.num_skills, is_train=False)

        knowledge_levels = self.model.predict(model_input)[0]
        return knowledge_levels
