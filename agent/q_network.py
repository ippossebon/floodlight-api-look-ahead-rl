## Rede neural + Q-Learning
# pkg_resources.require("tensorflow==1.15.2")
import tensorflow as tf

class QNetwork():
    def __init__(self, state_dim, action_size):
        self.state_in = tf.placeholder(tf.float32, shape=[None, 9]) # 9 é o numero de ações possiveis
        self.action_in = tf.placeholder(tf.int32, shape=[None])
        self.q_target_in = tf.placeholder(tf.float32, shape=[None])
        action_one_hot = tf.one_hot(self.action_in, depth=action_size)

        self.hidden1 = tf.layers.dense(self.state_in, 100, activation=tf.nn.relu)
        self.q_state = tf.layers.dense(self.hidden1, action_size, activation=None)
        self.q_state_action = tf.reduce_sum(tf.multiply(self.q_state, action_one_hot), axis=1) # axis=1 = coluna

        self.loss = tf.reduce_mean(tf.square(self.q_state_action - self.q_target_in))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(self.loss)

    def updateModel(self, session, state, action, q_target):
        feed = {self.state_in: state, self.action_in: action, self.q_target_in: q_target}
        session.run(self.optimizer, feed_dict=feed)

    def getQState(self, session, state):
        q_state = session.run(self.q_state, feed_dict={self.state_in: state})
        return q_state

#
# isadora state [array([-0.00092737,  0.04468767, -0.04492622, -0.02794201])]
# isadora self.state_in Tensor("Placeholder:0", shape=(?, 4), dtype=float32)
# isadora q_state [[-0.00099433  0.00972717]]
#
# isadora state [[700, 700, 0, 0, 0, 700, 0, 0, 700]]
# isadora self.state_in Tensor("Placeholder:0", shape=(?, 1, 9), dtype=float32)
#
# isadora state [array([700, 700,   0,   0,   0, 700,   0,   0, 700])]
# isadora self.state_in Tensor("Placeholder:0", shape=(?, 1, 9), dtype=float32)
