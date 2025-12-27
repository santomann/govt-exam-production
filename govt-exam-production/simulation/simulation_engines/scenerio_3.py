import mesa
import random
from math import ceil
from mesa.datacollection import DataCollector

class Aspirant(mesa.Agent):
    def __init__(self, model: mesa.Model, mean_talent=0.5, std_talent=0.1, **kwargs):
        super().__init__(model)
        
        # 1. Attributes: Talent & Finances
        self.innate_talent = random.gauss(mean_talent, std_talent)
        self.financial_runway = max(1, ceil(random.gauss(4, 1.5))) # Higher variance in wealth
        self.initial_runway = self.financial_runway 
        
        # 2. Age Logic (18-32)
        random_age = random.gauss(23, 2.5)
        self.age = int(max(18, min(32, random_age)))
        
        # 3. COACHING LOGIC (The 3 Tiers)
        # Elite: High Runway (>=6)
        # Mass: Medium Runway (2-5)
        # Self-Study: Low Runway (<2)
        if self.financial_runway >= 6:
            self.coaching_type = "Elite"
            self.burn_rate = 1.0  # Parents cover costs, standard burn
            self.learning_mean = 0.06
            self.learning_std = 0.02 # Low noise (Consistent)
            self.potential_cap = 1.0
            
        elif self.financial_runway >= 2:
            self.coaching_type = "Mass"
            self.burn_rate = 1.5  # Fees + Devices eat into runway faster
            self.learning_mean = 0.045 # Better than self-study...
            self.learning_std = 0.12  # ...but HIGH variance (Distraction risk)
            self.potential_cap = 0.95
            
        else:
            self.coaching_type = "Self"
            self.burn_rate = 1.0  # Survival mode
            self.learning_mean = 0.02
            self.learning_std = 0.02 # Slow but steady
            self.potential_cap = 0.85

        # Initial Score Setup
        raw_init = self.innate_talent + random.gauss(0, 0.05)
        self.capped_potential = min(self.potential_cap, raw_init)
        self.current_score = 300 * self.capped_potential
        
        # State
        self.status = "active"
        self.last_rank = None 
        self.rank_history = [] 
        self.stress = 0.0

    def step(self):
        if self.status != "active": return

        # --- PHASE 0: AGING ---
        self.age += 1 

        # --- PHASE 1: HARD STOPS ---
        if self.age > 32:
            self.status = "quit_age_limit"
            return
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
            
            # B. Gap Filter (Mass students tolerate more failure due to "Motivation")
            if self.last_rank > threshold:
                gap = self.last_rank - threshold
                tolerance_multiplier = 200 if self.coaching_type == "Mass" else 150
                tolerance = self.financial_runway * tolerance_multiplier
                if gap > tolerance:
                    self.status = "quit_gap"
                    return

        # --- PHASE 3: ACTION ---
        self.financial_runway -= self.burn_rate # Apply specific burn rate
        
        # LEARNING LOGIC (Mean + Noise)
        # We assume coaching impact is cumulative
        learning_noise = random.gauss(0, self.learning_std)
        actual_growth = self.learning_mean + learning_noise
        
        # Mass coaching risk: If growth is negative (distraction), we floor it at -0.01
        # (You can't unlearn too much, but you can waste a year)
        actual_growth = max(-0.01, actual_growth)
        
        experience_boost = len(self.rank_history) * actual_growth
        
        raw = self.innate_talent + experience_boost + random.gauss(0, 0.03)
        self.capped_potential = min(self.potential_cap, raw)
        self.current_score = 300 * self.capped_potential
        
        # Stress Calculation
        if self.last_rank:
            # Mass students have high stress due to FOMO (Fear Of Missing Out)
            base_stress = 0.4 if self.coaching_type == "Elite" else 0.7 if self.coaching_type == "Mass" else 0.6
            age_factor = (self.age - 20) * 0.05 
            self.stress += ((self.last_rank / self.model.num_agents) * base_stress) + age_factor

# --- HELPER FUNCTIONS ---
def get_average_stress(model):
    active = [a for a in model.agents if a.status == "active"]
    return sum(a.stress for a in active) / len(active) if active else 0.0

def get_average_age(model):
    active = [a for a in model.agents if a.status == "active"]
    return sum(a.age for a in active) / len(active) if active else 0.0

# --- NEW HELPERS FOR 3 TIERS ---
def get_elite_score(model):
    group = [a for a in model.agents if a.status == "active" and a.coaching_type == "Elite"]
    return sum(a.current_score for a in group) / len(group) if group else 0.0

def get_mass_score(model):
    group = [a for a in model.agents if a.status == "active" and a.coaching_type == "Mass"]
    return sum(a.current_score for a in group) / len(group) if group else 0.0

def get_self_score(model):
    group = [a for a in model.agents if a.status == "active" and a.coaching_type == "Self"]
    return sum(a.current_score for a in group) / len(group) if group else 0.0

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
                "Elite_Score": get_elite_score,
                "Mass_Score": get_mass_score,
                "Self_Score": get_self_score,
                "Average Age": get_average_age
            },
            agent_reporters={
                "Score": "current_score", 
                "Potential": "capped_potential", 
                "Age": "age", 
                "Runway": "initial_runway", 
                "Coaching": "coaching_type", # Updated to String
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