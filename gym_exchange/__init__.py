from gym.envs.registration import register

register(
    id='Snake-v0',
    entry_point='gym_exchange.envs:ExchangeEnv',
)