# Reinforcement Learning for Supply Chain Optimization

## Overview

This document describes the reinforcement learning (RL) implementation for dynamic supply chain optimization in the multi-domain supply chain and finance platform. The RL system uses advanced algorithms to optimize inventory management, dynamic pricing, supplier selection, and logistics routing.

## Implemented Algorithms

### 1. Deep Q-Network (DQN)
- Standard DQN with experience replay and target network
- Epsilon-greedy exploration strategy
- Suitable for discrete action spaces

### 2. Proximal Policy Optimization (PPO)
- Actor-Critic architecture for more stable training
- Clipped surrogate objective for policy updates
- Better sample efficiency than DQN
- Suitable for both discrete and continuous action spaces

### 3. Multi-Agent RL System
- Independent learning for multiple supply chain entities
- Coordinated decision making across the supply chain
- Scalable to large supply chain networks

## Key Features

1. **Inventory Management Optimization**
   - Dynamic order quantity decisions
   - Balancing holding costs and stockout costs
   - Adaptive to demand patterns

2. **Dynamic Pricing Strategies**
   - Price optimization based on demand elasticity
   - Competitive pricing adjustments
   - Revenue maximization

3. **Supplier Selection and Management**
   - Dynamic supplier switching based on performance
   - Risk-aware supplier selection
   - Cost optimization

4. **Route Optimization for Logistics**
   - Dynamic route planning
   - Traffic and weather adaptation
   - Delivery time optimization

## Architecture

### Core Components

1. **SupplyChainEnvironment**
   - Simulates supply chain dynamics
   - Provides state, reward, and transition functions
   - Configurable parameters for different scenarios

2. **SupplyChainDQNAgent**
   - Implements DQN algorithm
   - Experience replay buffer
   - Target network updates

3. **SupplyChainPPOAgent**
   - Implements PPO algorithm
   - Actor-Critic architecture
   - Clipped policy updates

4. **MultiAgentSupplyChain**
   - Coordinates multiple RL agents
   - Independent learning with shared environment
   - Scalable architecture

## API Endpoints

### Train RL Model for Inventory Optimization
```
POST /api/ai/rl/train-inventory
Body: {"n_episodes": 1000, "max_steps": 365, "state_dim": 2, "action_dim": 10}
```

### Optimize Supply Chain with RL
```
POST /api/ai/rl/optimize
Body: {"state": [0.5, 0.2]}
```

### Multi-Agent Supply Chain Optimization
```
POST /api/ai/rl/multi-agent-optimize
Body: {"states": [[0.5, 0.2], [0.3, 0.7], [0.8, 0.1]]}
```

### Get RL Model Performance
```
GET /api/ai/rl/performance
```

### Retrain RL Models
```
POST /api/ai/rl/models/retrain
```

## Implementation Files

1. `ai-ml/src/supply_chain_rl.py` - Core RL implementation
2. `backend/ai-service/src/main/java/com/app/ai/service/ReinforcementLearningService.java` - Java service integration
3. `backend/ai-service/src/main/java/com/app/ai/controller/AIController.java` - API endpoints

## Usage Examples

### Python Example
```python
# Initialize environment
env = SupplyChainEnvironment()

# Create PPO agent
agent = SupplyChainPPOAgent(state_dim=2, action_dim=10)

# Training loop
for episode in range(1000):
    state = env.reset()
    for step in range(365):
        action, log_prob = agent.act(state)
        next_state, reward, done, info = env.step(action)
        agent.remember(state, action, reward, next_state, log_prob, done)
        if done:
            break
    if episode % 10 == 0:
        agent.update()

# Save model
agent.save_model("supply_chain_ppo_model.pth")
```

### Java Example
```java
@Autowired
private ReinforcementLearningService rlService;

// Train inventory optimization model
Map<String, Object> parameters = new HashMap<>();
parameters.put("n_episodes", 1000);
parameters.put("max_steps", 365);
Map<String, Object> results = rlService.trainInventoryOptimization(
    new ObjectMapper().writeValueAsString(parameters));

// Optimize supply chain
String currentState = "[0.5, 0.2]";
Map<String, Object> optimizationResults = rlService.optimizeSupplyChain(currentState);
```

## Training Process

1. **Environment Setup**
   - Define state and action spaces
   - Configure reward function
   - Set simulation parameters

2. **Agent Initialization**
   - Select algorithm (DQN or PPO)
   - Configure hyperparameters
   - Initialize neural networks

3. **Training Loop**
   - Episode-based training
   - Experience collection
   - Periodic model updates
   - Performance monitoring

4. **Model Evaluation**
   - Test on validation environments
   - Performance metrics calculation
   - Model saving

## Performance Metrics

- Average reward per episode
- Convergence rate
- Exploration-exploitation balance
- Sample efficiency
- Generalization to new scenarios

## Configuration Parameters

### DQN Parameters
- Learning rate: 0.001
- Discount factor (gamma): 0.99
- Epsilon decay: 0.995
- Target network update frequency: 100 steps

### PPO Parameters
- Learning rate: 0.001
- Discount factor (gamma): 0.99
- Clipping parameter (epsilon): 0.2
- Number of epochs: 10

### Environment Parameters
- Initial inventory: 1000 units
- Maximum order quantity: 200 units
- Holding cost: $0.5 per unit per day
- Stockout cost: $10 per unit

## Future Enhancements

1. **Advanced Algorithms**
   - Soft Actor-Critic (SAC) for continuous control
   - Rainbow DQN with distributional RL
   - Hierarchical RL for complex decision making

2. **Multi-Agent Coordination**
   - Communication protocols between agents
   - Centralized training with decentralized execution
   - Game-theoretic approaches

3. **Transfer Learning**
   - Pre-trained models for new supply chains
   - Domain adaptation techniques
   - Few-shot learning capabilities

4. **Real-Time Learning**
   - Online learning from live data
   - Continuous model updates
   - Adaptive hyperparameters

## Conclusion

The reinforcement learning system provides advanced capabilities for dynamic supply chain optimization, enabling automated decision making that adapts to changing conditions and optimizes key performance metrics. The modular design allows for easy extension and integration with existing systems.