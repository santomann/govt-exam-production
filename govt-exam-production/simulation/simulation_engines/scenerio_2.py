import mesa
import random
from math import ceil
from mesa.datacollection import DataCollector

class Aspirant(mesa.Agent):
    def __init__(self, model: mesa.Model, mean_talent=0.5, std_talent=0.1, **kwargs):
        super().__init__(model)
        
        # 1. Attributes: Talent & Finances
        self.innate_talent = random.gauss(mean_talent, std_talent)
        self.financial_runway = max(1, ceil(random.gauss(4, 1)))
        self.initial_runway = self.financial_runway 
        
        # --- NEW: AGE LOGIC ---
        # Generate random age between 18 and 32
        # We assume Mean=23 (Fresh graduates), Std=2.5
        # This creates a bell curve where most are 21-25, fewer are 18 or 30+
        random_age = random.gauss(
            23, 2.5)
        self.age = int(max(18, min(32, random_age))) # Clip to ensure 18-32 range
        
        # Willingness to over-commit (random, independent of talent)
        self.is_overcommitted = (
            self.initial_runway <= 4 and random.random() < 0.25
        )

        # Coaching access
        self.has_elite_coaching = (
            self.initial_runway >= 5 or self.is_overcommitted
        )

        # Initial Score Setup
        raw_init = self.innate_talent + random.gauss(0, 0.05)
        self.capped_potential = min(1.0, raw_init)
        self.current_score = 300 * self.capped_potential
        
        # State
        self.status = "active"
        self.last_rank = None 
        self.rank_history = [] 
        self.stress = 0.0

    def step(self):
        if self.status != "active": return

        # --- PHASE 0: AGING ---
        self.age += 1 # Everyone gets older

        # --- PHASE 1: HARD STOPS (Money OR Age) ---
        
        # CHECK 1: Age Limit
        if self.age > 32:
            self.status = "quit_age_limit"
            # Optional: Print for debugging
            # print(f"Agent {self.unique_id}: Aged out at {self.age}")
            return

        # CHECK 2: Money Limit
        if self.financial_runway <= 0:
            self.status = "quit_financial"
            return

        # --- PHASE 2: SOFT STOPS (Potential) ---
        threshold = self.model.top_n_seats * 10
        if self.last_rank:
            # A. Hopeless Filter
            if len(self.rank_history) >= 3:
                recent = self.rank_history[-3:]
                if sum(1 for r in recent if r > threshold) == 3:
                    self.status = "quit_potential"
                    return
            
            # B. Gap Filter
            if self.last_rank > threshold:
                gap = self.last_rank - threshold
                tolerance = self.financial_runway * 150 
                if gap > tolerance:
                    self.status = "quit_gap"
                    return
                
        burn_rate = 2 if self.is_overcommitted else 1
        self.financial_runway -= burn_rate

        # --- PHASE 3: ACTION ---
        self.financial_runway -= 1
        
        # Elite Boost Calculation
        learning_rate = 0.06 if self.has_elite_coaching else 0.02
        experience_boost = len(self.rank_history) * learning_rate
        
        raw = self.innate_talent + experience_boost + random.gauss(0, 0.05)
        self.capped_potential = min(1.0, raw)
        self.current_score = 300 * self.capped_potential
        
        # Stress Calculation (Stress increases with Age too now!)
        if self.last_rank:
            stress_multiplier = (
                0.35 if self.has_elite_coaching and not self.is_overcommitted
                else 0.8 if self.is_overcommitted
                else 0.6
            )
            age_factor = (self.age - 20) * 0.05 
            self.stress += ((self.last_rank / self.model.num_agents) * stress_multiplier) + age_factor

# --- HELPER FUNCTIONS ---
def get_average_stress(model):
    active = [a for a in model.agents if a.status == "active"]
    return sum(a.stress for a in active) / len(active) if active else 0.0

def get_rich_score(model):
    rich = [a for a in model.agents if a.status == "active" and a.initial_runway >= 6]
    return sum(a.current_score for a in rich) / len(rich) if rich else 0.0

def get_poor_score(model):
    poor = [a for a in model.agents if a.status == "active" and a.initial_runway < 4]
    return sum(a.current_score for a in poor) / len(poor) if poor else 0.0

# NEW HELPER: Track Average Age of Competitors
def get_average_age(model):
    active = [a for a in model.agents if a.status == "active"]
    return sum(a.age for a in active) / len(active) if active else 0.0

class ExamEcosystem(mesa.Model):
    def __init__(self, num_agents, top_n_seats, growth_rate=0.03, **agent_kwargs):
        super().__init__()
        self.num_agents = num_agents
        self.top_n_seats = top_n_seats
        self.growth_rate = growth_rate
        self.cutoff_score = 0.0
        self.agent_kwargs_memory = agent_kwargs 
        
        Aspirant.create_agents(self, num_agents, **agent_kwargs)

        self.datacollector = DataCollector(
            model_reporters={
                "Average Stress": get_average_stress,
                "Cutoff Score": "cutoff_score",
                "Active Agents": lambda m: len([a for a in m.agents if a.status == "active"]),
                "Rich_score": get_rich_score,
                "Poor_score": get_poor_score,
                "Average Age": get_average_age # <--- Added this
            },
            # Added "Age" to agent reporters
           agent_reporters={
                "Score": "current_score", 
                "Potential": "capped_potential", 
                "Age": "age", 
                "Runway": "initial_runway", 
                "Coaching": "has_elite_coaching",
                "Talent": "innate_talent",
                "Status": "status" 
            }
        )

    def step(self):
        self.agents.shuffle_do("step")

        # Rank & Select
        active = [a for a in self.agents if a.status == "active"]
        if active:
            active.sort(key=lambda x: x.current_score, reverse=True)
            for rank, agent in enumerate(active, start=1):
                agent.last_rank = rank
                agent.rank_history.append(rank)
                if rank <= self.top_n_seats:
                    agent.status = "selected"

            if len(active) >= self.top_n_seats:
                self.cutoff_score = active[self.top_n_seats - 1].current_score
            else:
                self.cutoff_score = 0

        # Population Growth
        self.num_agents = int(self.num_agents * (1 + self.growth_rate))
        current_active = len([a for a in self.agents if a.status == "active"])
        spots_to_fill = self.num_agents - current_active
        
        if spots_to_fill > 0:
            Aspirant.create_agents(self, spots_to_fill, **self.agent_kwargs_memory)


        self.datacollector.collect(self)
        df = self.datacollector.get_agent_vars_dataframe()
        print(df)



if __name__ == "__main__":
    # Test in terminal
    print("--- STARTING 300-MARK SIMULATION ---")
    model = ExamEcosystem(num_agents=2000, top_n_seats=50)
    
    for i in range(5):
        print(f"\n--- YEAR {i+1} ---")
        model.step()
        stats = model.datacollector.get_model_vars_dataframe().iloc[-1]
        print(f"Stats -> Cutoff: {stats['Cutoff Score']:.2f} | Active: {stats['Active Agents']}")
    
    