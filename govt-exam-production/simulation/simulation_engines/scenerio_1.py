import mesa
import random
from math import ceil
from mesa.datacollection import DataCollector

class Aspirant(mesa.Agent):
    def __init__(self, model: mesa.Model, mean_talent=0.5, std_talent=0.1, **kwargs):
        super().__init__(model)
        
        # 1. Attributes
        self.innate_talent = random.gauss(mean_talent, std_talent)
        
 
        self.financial_runway = max(1, ceil(random.gauss(4, 1)))
        raw_init = self.innate_talent + random.gauss(0, 0.05)  #the random gauss will provide negatices as well - this is intentional
        self.capped_potential = min(1.0, raw_init)
        self.current_score = 300 * self.capped_potential
    
        # Save initial for the "Rich/Poor" analysis later
        self.initial_runway = self.financial_runway 
        
        # 2. State
        self.status = "active"
        self.last_rank = None 
        self.rank_history = [] 
        self.stress = 0.0

    def step(self):
        if self.status != "active":
            return

        # --- PHASE 1: HARD STOP ---
        if self.financial_runway <= 0:
            self.status = "quit_financial"
            return

        # --- PHASE 2: SOFT STOP ---
        threshold = self.model.top_n_seats * 10
        if self.last_rank:
            # Check 3-year failure
            if len(self.rank_history) >= 3:
                recent = self.rank_history[-3:]
                if sum(1 for r in recent if r > threshold) == 3:
                    self.status = "quit_potential"
                    return
            # Check Gap
            if self.last_rank > threshold:
                gap = self.last_rank - threshold
                # If gap is huge (500 ranks) and money is low (1 year), quit.
                if gap > (self.financial_runway * 100):
                    self.status = "quit_gap"
                    return

        # --- PHASE 3: ACTION ---
        self.financial_runway -= 1
        
        # Experience Calculation
        exp_boost = len(self.rank_history) * 0.04
        raw = self.innate_talent + exp_boost + random.gauss(0, 0.05)
        
        # Store Potential
        self.capped_potential = min(1.0, raw)
        
        # Calculate Score
        self.current_score = 300 * self.capped_potential

        
        # Calculate Stress // stress is only there if an agent has given an exam last year
        if self.last_rank:
            self.stress += (self.last_rank / self.model.num_agents) * 0.5

# --- HELPER FUNCTIONS WITH SAFETY CHECKS ---
def get_average_stress(model):
    active = [a for a in model.agents if a.status == "active"]
    return sum(a.stress for a in active) / len(active) if active else 0.0

def get_rich_score(model):
    # Rich = Initial Runway > 5
    rich = [a for a in model.agents if a.status == "active" and a.initial_runway > 5]
    return sum(a.current_score for a in rich) / len(rich) if rich else 0.0

def get_poor_score(model):
    # Poor = Initial Runway < 3
    poor = [a for a in model.agents if a.status == "active" and a.initial_runway < 3]
    return sum(a.current_score for a in poor) / len(poor) if poor else 0.0

class ExamEcosystem(mesa.Model):
    def __init__(self, num_agents=2000, top_n_seats=50, **agent_kwargs):
        super().__init__()
        self.num_agents = num_agents
        self.top_n_seats = top_n_seats
        self.cutoff_score = 0.0
        
        # MEMORY: Save args to create new agents later
        self.agent_kwargs_memory = agent_kwargs 
        
        # Create Initial Agents
        Aspirant.create_agents(self, num_agents, **agent_kwargs)

        
        self.datacollector = DataCollector(
            model_reporters={
                "Average Stress": get_average_stress,
                "Cutoff Score": "cutoff_score",
                "Active Agents": lambda m: len([a for a in m.agents if a.status == "active"]),
                "Rich_score": get_rich_score,
                "Poor_score": get_poor_score
            },
            # Collect "Potential" for the histogram
            agent_reporters={"Score": "current_score", "Potential": "capped_potential"}
        )

    def step(self):
        # 1. Agents Act
        self.agents.shuffle_do("step")

        # 2. Rank & Select
        active = [a for a in self.agents if a.status == "active"]
        if active:
            active.sort(key=lambda x: x.current_score, reverse=True)
            for rank, agent in enumerate(active, start=1):
                agent.last_rank = rank
                agent.rank_history.append(rank)
                if rank <= self.top_n_seats:
                    agent.status = "selected"

            # Set Cutoff
            if len(active) >= self.top_n_seats:
                self.cutoff_score = active[self.top_n_seats - 1].current_score
            else:
                self.cutoff_score = 0

        # 3. REPLENISHMENT (Crucial Logic!)
        current_count = len([a for a in self.agents if a.status == "active"])
        missing_spots = self.num_agents - current_count
        
        if missing_spots > 0:
            # Add fresh agents to replace those who quit/passed
            Aspirant.create_agents(self, missing_spots, **self.agent_kwargs_memory)

        # 4. Collect Data

        self.datacollector.collect(self)


if __name__ == "__main__":
    # Test in terminal
    print("--- STARTING 300-MARK SIMULATION ---")
    model = ExamEcosystem(num_agents=2000, top_n_seats=50)
    
    for i in range(5):
        print(f"\n--- YEAR {i+1} ---")
        model.step()
        stats = model.datacollector.get_model_vars_dataframe().iloc[-1]
        print(f"Stats -> Cutoff: {stats['Cutoff Score']:.2f} | Active: {stats['Active Agents']}")
    