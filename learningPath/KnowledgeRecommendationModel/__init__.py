import os
import numpy as np

from learningPath.A2C.a2c import A2C


file_path, _ = os.path.split(os.path.realpath(__file__))

MODEL_CONFIG = {
    'ASSISTment2009-2010': {
        'act_dim': 111,
        'state_dim': (111,),
        'consecutive_frames': 20,
        'actor_path': os.path.join(file_path, './model/checkpoint_46200_score_10.884216263457775_LR_0.0001_actor.h5'),
        'critic_path': os.path.join(file_path, './model/checkpoint_46200_score_10.884216263457775_LR_0.0001_critic.h5'),
    }
}


class KnowledgeRecommendationModel:
    def __init__(self, course_name):
        act_dim = MODEL_CONFIG[course_name]['act_dim']
        state_dim = MODEL_CONFIG[course_name]['state_dim']
        consecutive_frames = MODEL_CONFIG[course_name]['consecutive_frames']
        actor_path = MODEL_CONFIG[course_name]['actor_path']
        critic_path = MODEL_CONFIG[course_name]['critic_path']

        self.model = A2C(act_dim, state_dim, consecutive_frames)
        self.model.load_weights(actor_path, critic_path)

    def recommend(self, states):
        action = self.model.policy_action(np.expand_dims(states, axis=0), None)
        return action
