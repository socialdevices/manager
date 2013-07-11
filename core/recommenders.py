import logging
import random
logging.getLogger(__name__)


class Recommender:
    RANDOM_SELECT = 1
    
    def __init__(self, policy=None, selector=None):
        self.policy = policy or DefaultPolicy()   
        self.selector = selector or self.RANDOM_SELECT
        
    def recommend( self, configurations ):
        if self.policy:
            ranked = self.policy.evaluate(configurations)

            if self.selector == Recommender.RANDOM_SELECT:
                max_rank = ranked[0]['rank']
                return random.choice( [conf for conf in ranked if conf['rank']==max_rank] )
        else:
            raise RecommenderException('Recommender has no policy')
        
    def getPolicy( self ):
        if self.policy:
            return self.policy
        else:
            raise RecommenderException('Recommender has no policy')
        
class RecommenderException(Exception):
    pass
    
class DefaultPolicy:
    def __init__(self):
        pass

    def _order_by_rank( self, configurations ):
        return sorted( configurations, key = lambda c: c['rank'], reverse=True )
    
    def evaluate(self, configurations):
        
        for configuration in configurations:
            if 'roles' in configuration.keys():
                configuration['rank'] = len(configuration['roles'])
        
        return self._order_by_rank( configurations )
