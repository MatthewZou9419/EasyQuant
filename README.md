# EasyQuant
Easy quant platform by Matt.
* Database
* Strategies(Focus more on risk management & position sizing)
* Portfolio & Order management
* Risk & Position management
* Execution(Not considered yet)
* Performance & Reporting


# Demo
    from EasyEngine.EStrategyTarget import Strategy
    
    class StrategyDemo(Strategy):
        def initialize(self, context):  # execute at the very beginning
            pass
            
        def handle_data(self, context):  # execute at every bar
            pass
        
