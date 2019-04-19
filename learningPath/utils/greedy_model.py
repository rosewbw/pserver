import os
import tensorflow as tf
import numpy as np

from .utils import DKT
from .load_data import OriginalInputProcessor

file_path, _ = os.path.split(os.path.realpath(__file__))
knowledge_tracing_model_path = os.path.join(file_path, 'model/LSTM-200')

num_skills = 111

input_processor = OriginalInputProcessor()


class Greedy_model:
    def __init__(self, act_dim, env_dim):
        self.act_dim = act_dim
        self.env_dim = env_dim

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
        # tf.reset_default_graph()
        with self.graph.as_default():
            self.model = DKT(self.sess, None, None, num_skills, network_config)
            self.model.model.build_graph()
            self.model.load_model(knowledge_tracing_model_path)

    def predict(self, learning_history):
        problem_seqs = [[problem for (problem, correct) in learning_history]]
        correct_seqs = [[correct for (problem, correct) in learning_history]]
        model_input, _, _ = input_processor.process_problems_and_corrects(problem_seqs, correct_seqs, num_skills, is_train=False)

        next_observation = self.model.predict(model_input)[0][-1]
        return next_observation

    def __predict_correct(self, learning_history, action):
        correct_rate = self.predict(learning_history)[action]
        p = np.array([1 - correct_rate, correct_rate])
        return np.random.choice([0, 1], p=p.ravel())

    def predict_action(self, learning_history, action):
        """
        根据输入的 action 结合之前的 learning_history 判断学习情况
        """
        fake_history = [i for i in learning_history]
        fake_history.append((action, self.__predict_correct(learning_history, action)))
        return self.predict(fake_history)

    def policy_action(self, s, learning_history):
        """
        对所有 action 都试一次，取总 reward 最高的
        """
        current_states = self.predict(learning_history)
        estimated_reward_states = []
        for action in range(num_skills):
            estimated_states = self.predict_action(learning_history, action)
            estimated_reward_states.append(estimated_states[action] - current_states[action])

        return np.argmax(estimated_reward_states)

    def reset(self):
        pass
