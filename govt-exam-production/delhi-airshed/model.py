from mesa import Model
from agent import PollutionHub
import random
import math

class DelhiAirshed(Model):
    """
    The Holistic World Model (Daily Timescale).
    Controls Regional Meteorology, Inter-Zone Transport, and Temporal Events.
    
    Accepts optional custom_params for full user control over all parameters.
    """
    def __init__(self, start_month="Nov", start_day=1, custom_params=None):
        super().__init__()
        
        # Store custom parameters
        self.custom_params = custom_params
        
        # --- 1. TEMPORAL STATE ---
        self.current_day = start_day
        self.month = start_month
        self.day_of_week = self.get_day_of_week(start_day)
        
        # --- 2. REGIONAL METEOROLOGY (NCR-Wide) ---
        if custom_params and 'init_wind_speed' in custom_params:
            self.regional_wind_speed = custom_params['init_wind_speed']
            self.regional_wind_direction = custom_params.get('init_wind_dir', 'NW')
        else:
            self.regional_wind_speed = 3.0
            self.regional_wind_direction = 'NW'
        
        wind_map = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}
        self.regional_wind_bearing = wind_map.get(self.regional_wind_direction, 315)
        self.base_mixing_height = 400
        self.daily_avg_temp = 20.0
        
        # Persistence Logic
        self.days_in_current_pattern = 0
        self.days_until_wind_change = random.randint(2, 5)
        self.days_since_rain = 0
        
        # Regional Events
        self.stubble_fire_count = 0
        self.rain_occurred = False
        
        # --- 3. INITIALIZE ZONES ---
        self.init_zones()
        
        # Initial Weather Setup
        self.update_seasonal_baseline()

    def init_zones(self):
        """Creates the 5 zones with optional custom parameters"""
        
        # Default configurations
        default_configs = [
            {
                'name': 'Anand Vihar', 'lat': 28.647, 'lon': 77.301, 'type': 'industrial_edge',
                'congestion': 2.8, 'silt': 6.0, 'ind_dist': 3, 'const': 150, 'fires': 500,
                'uhi': 0.8, 'water': 0.7, 'density': 0.75,
                'vehicles': {'trucks': {'count': 14000, 'avg_stay_hrs': 1}, 
                            'buses': {'count': 15000, 'avg_stay_hrs': 1}, 
                            'cars': {'count': 50000, 'avg_stay_hrs': 1.4}, 
                            'two_wheelers': {'count': 60000, 'avg_stay_hrs': 1.2}, 
                            'autos': {'count': 20000, 'avg_stay_hrs': 1.5}}
            },
            {
                'name': 'Lutyens Delhi', 'lat': 28.614, 'lon': 77.209, 'type': 'vip',
                'congestion': 2, 'silt': 2, 'ind_dist': 30, 'const': 50, 'fires': 50,
                'uhi': 0.5, 'water': 0.0, 'density': 0.4,
                'vehicles': {'trucks': {'count': 1500, 'avg_stay_hrs': 0.8}, 
                            'buses': {'count': 6000, 'avg_stay_hrs': 0.8}, 
                            'cars': {'count': 80000, 'avg_stay_hrs': 1.2}, 
                            'two_wheelers': {'count': 40000, 'avg_stay_hrs': 0.8}, 
                            'autos': {'count': 9000, 'avg_stay_hrs': 0.8}}
            },
            {
                'name': 'Okhla', 'lat': 28.532, 'lon': 77.273, 'type': 'industrial_core',
                'congestion': 2.5, 'silt': 4.5, 'ind_dist': 2, 'const': 200, 'fires': 700,
                'uhi': 0.7, 'water': 0.8, 'density': 0.65,
                'vehicles': {'trucks': {'count': 18000, 'avg_stay_hrs': 2.0}, 
                            'buses': {'count': 10000, 'avg_stay_hrs': 0.6}, 
                            'cars': {'count': 35000, 'avg_stay_hrs': 1.5}, 
                            'two_wheelers': {'count': 70000, 'avg_stay_hrs': 2.0}, 
                            'autos': {'count': 18000, 'avg_stay_hrs': 1.5}}
            },
            {
                'name': 'Uttam Nagar', 'lat': 28.622, 'lon': 77.059, 'type': 'residential_dense',
                'congestion': 3.0, 'silt': 5.5, 'ind_dist': 15, 'const': 180, 'fires': 1000,
                'uhi': 0.9, 'water': 0.1, 'density': 0.9,
                'vehicles': {'trucks': {'count': 10000, 'avg_stay_hrs': 1}, 
                            'buses': {'count': 40000, 'avg_stay_hrs': 1.5}, 
                            'cars': {'count': 30000, 'avg_stay_hrs': 2.0}, 
                            'two_wheelers': {'count': 100000, 'avg_stay_hrs': 2.5}, 
                            'autos': {'count': 25000, 'avg_stay_hrs': 2.0}}
            },
            {
                'name': 'Bahadurgarh', 'lat': 28.693, 'lon': 76.920, 'type': 'periurban',
                'congestion': 2.5, 'silt': 7.0, 'ind_dist': 1, 'const': 250, 'fires': 400,
                'uhi': 0.6, 'water': 0.2, 'density': 0.6,
                'vehicles': {'trucks': {'count': 15000, 'avg_stay_hrs': 1.5}, 
                            'buses': {'count': 18000, 'avg_stay_hrs': 0.6}, 
                            'cars': {'count': 40000, 'avg_stay_hrs': 1.8}, 
                            'two_wheelers': {'count': 55000, 'avg_stay_hrs': 1.2}, 
                            'autos': {'count': 15000, 'avg_stay_hrs': 1.2}}
            }
        ]

        for i, default_cfg in enumerate(default_configs):
            # Use custom params if provided, else use defaults
            if self.custom_params and 'zones' in self.custom_params:
                zone_name = default_cfg['name']
                if zone_name in self.custom_params['zones']:
                    custom_zone = self.custom_params['zones'][zone_name]
                    cfg = {
                        'name': zone_name,
                        'lat': default_cfg['lat'],
                        'lon': default_cfg['lon'],
                        'type': default_cfg['type'],
                        'congestion': custom_zone.get('congestion', default_cfg['congestion']),
                        'silt': custom_zone.get('silt', default_cfg['silt']),
                        'ind_dist': custom_zone.get('ind_dist', default_cfg['ind_dist']),
                        'const': custom_zone.get('const', default_cfg['const']),
                        'fires': custom_zone.get('fires', default_cfg['fires']),
                        'vehicles': custom_zone.get('vehicles', default_cfg['vehicles']),
                        'uhi': default_cfg['uhi'],
                        'water': default_cfg['water'],
                        'density': default_cfg['density']
                    }
                else:
                    cfg = default_cfg
            else:
                cfg = default_cfg
            
            # Create agent
            a = PollutionHub(
                unique_id=i+1, model=self, name=cfg['name'],
                vehicle_data=cfg['vehicles'],
                congestion_level=cfg['congestion'],
                road_silt=cfg['silt'], 
                dist_to_industry=cfg['ind_dist'],
                garbage_fires=cfg['fires'], 
                const_sites=cfg['const'],
                zone_type=cfg['type'], 
                location={'lat': cfg['lat'], 'lon': cfg['lon']}
            )
            a.urban_heat_island_factor = cfg['uhi']
            a.water_proximity = cfg['water']
            a.building_density = cfg['density']
            
            # Initialize Dynamic State
            a.mixing_height = 400
            a.wind_speed = 3.0
            a.is_foggy = False
            a.external_load_kg = 0.0
            a.pm25_concentration = 0.0

    def step(self):
        """Advance the World by 1 DAY"""
        # 1. Update Calendar
        self.current_day += 1
        if self.current_day > 30: 
            self.current_day = 1
            self.month = self.next_month(self.month)
        self.day_of_week = self.get_day_of_week(self.current_day)

        # 2. Update Regional Meteorology
        self.update_regional_meteorology()
        self.update_stubble_fires()
        self.rain_occurred = self.check_rain_event()

        # 3. Update Zone-Specific Meteorology
        for agent in self.agents:
            self.calculate_zone_meteorology(agent)
            agent.emission_multiplier = self.get_weekly_emission_multiplier(agent)

        # 4. Execute Step
        self.agents.do("step")

        # 5. Apply Rain Washout
        if self.rain_occurred:
            self.apply_rain_washout()

        # 6. Execute Advance
        self.agents.do("advance")

    def update_regional_meteorology(self):
        self.update_seasonal_baseline()
        self.days_in_current_pattern += 1
        
        if self.days_in_current_pattern > self.days_until_wind_change:
            self.days_in_current_pattern = 0
            self.days_until_wind_change = random.randint(2, 5)
            self.randomize_regional_wind()
        else:
            self.regional_wind_speed *= random.uniform(0.8, 1.2)

    def update_seasonal_baseline(self):
        """Set base mixing height from custom params or defaults"""
        if self.custom_params and 'mixing_heights' in self.custom_params:
            mix_map = self.custom_params['mixing_heights']
        else:
            mix_map = {
                'Jan': 300, 'Feb': 400, 'Mar': 800, 'Apr': 1200, 
                'May': 1500, 'Jun': 1000, 'Jul': 800, 'Aug': 800, 
                'Sep': 900, 'Oct': 700, 'Nov': 400, 'Dec': 250
            }
        self.base_mixing_height = mix_map.get(self.month, 500)
        
        # Fog probability
        if self.custom_params and 'fog_probs' in self.custom_params:
            fog_prob_map = self.custom_params['fog_probs']
            self.base_fog_prob = fog_prob_map.get(self.month, 0.0)
        else:
            fog_prob_map = {'Jan': 0.7, 'Dec': 0.8, 'Nov': 0.6, 'Feb': 0.5, 'Oct': 0.2, 'Mar': 0.1}
            self.base_fog_prob = fog_prob_map.get(self.month, 0.0)

    def randomize_regional_wind(self):
        if self.month in ['Nov', 'Dec', 'Jan', 'Feb']:
            dirs = ['NW', 'N', 'W']; weights = [0.6, 0.25, 0.15]
            avg_speed = random.uniform(2.0, 8.0) 
        elif self.month in ['Mar', 'Apr', 'May']:
            dirs = ['W', 'NW', 'SW', 'N']; weights = [0.4, 0.3, 0.2, 0.1]
            avg_speed = random.uniform(8.0, 20.0) 
        elif self.month in ['Jun', 'Jul', 'Aug', 'Sep']:
            dirs = ['SE', 'E', 'S']; weights = [0.5, 0.3, 0.2]
            avg_speed = random.uniform(5.0, 15.0) 
        else:
            dirs = ['NW', 'N', 'E', 'W']; weights = [0.4, 0.3, 0.2, 0.1]
            avg_speed = random.uniform(3.0, 10.0)

        self.regional_wind_direction = random.choices(dirs, weights)[0]
        self.regional_wind_speed = avg_speed
        
        wind_map = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}
        self.regional_wind_bearing = wind_map.get(self.regional_wind_direction, 315)

    def calculate_zone_meteorology(self, zone):
        """Calculate zone-specific meteorology"""
        
        # Night & day mixing heights
        night_base = {
            'Jan': 100, 'Feb': 150, 'Mar': 200, 'Apr': 300, 'May': 350, 'Jun': 250,
            'Jul': 200, 'Aug': 200, 'Sep': 250, 'Oct': 200, 'Nov': 150, 'Dec': 120
        }
        h_night = night_base.get(self.month, 200)
        
        day_base = {
            'Jan': 350, 'Feb': 500, 'Mar': 900, 'Apr': 1400, 'May': 1800, 'Jun': 1200,
            'Jul': 900, 'Aug': 900, 'Sep': 1000, 'Oct': 800, 'Nov': 500, 'Dec': 400
        }
        h_day = day_base.get(self.month, 600)
        
        h_daily_avg = (h_night * 12 + h_day * 12) / 24
        
        # Zone-specific modifiers
        uhi_bonus = zone.urban_heat_island_factor * 80
        water_penalty = zone.water_proximity * (-60)
        daily_var = random.uniform(-40, 40)
        wind_boost = min(50, max(0, (self.regional_wind_speed - 3) * 10))
        cloud_penalty = -80 if (random.random() < self.base_fog_prob) else 0
        
        zone_height = h_daily_avg + uhi_bonus + water_penalty + wind_boost + cloud_penalty + daily_var
        zone.mixing_height = max(100, min(zone_height, 2500))
        
        # Wind speed
        friction = 1.0 - (zone.building_density * 0.5)
        zone.wind_speed = max(0.5, self.regional_wind_speed * friction)
        zone.wind_dir = self.regional_wind_direction
        
        # Fog
        wind_factor = -0.4 if self.regional_wind_speed > 10 else (0.2 if self.regional_wind_speed < 3 else 0.0)
        water_factor = zone.water_proximity * 0.2
        uhi_factor = zone.urban_heat_island_factor * (-0.2)
        
        total_prob = self.base_fog_prob + wind_factor + water_factor + uhi_factor
        total_prob = max(0, min(1.0, total_prob))
        
        zone.is_foggy = (random.random() < total_prob)

    def update_stubble_fires(self):
        """Update stubble fire count"""
        # Check if stubble is enabled
        if self.custom_params and not self.custom_params.get('enable_stubble', True):
            self.stubble_fire_count = 0
            return
        
        # Base fire counts
        if self.month == 'Nov' and self.current_day <= 10:
            base_fires = random.randint(3000, 7000)
        elif self.month == 'Oct' and self.current_day >= 20:
            base_fires = random.randint(1500, 4000)
        elif self.month == 'Nov' and self.current_day <= 20:
            base_fires = random.randint(500, 2000)
        else:
            base_fires = random.randint(0, 100)
        
        # Apply multiplier if custom
        if self.custom_params and 'stubble_multiplier' in self.custom_params:
            base_fires = int(base_fires * self.custom_params['stubble_multiplier'])
        
        self.stubble_fire_count = base_fires

    def check_rain_event(self):
        """Check for rain with optional custom probabilities"""
        if self.custom_params and not self.custom_params.get('enable_rain', True):
            self.days_since_rain += 1
            return False
        
        rain_map = {'Jan': 0.05, 'Feb': 0.08, 'Mar': 0.1, 'Apr': 0.05,
                    'May': 0.1, 'Jun': 0.3, 'Jul': 0.7, 'Aug': 0.7,
                    'Sep': 0.4, 'Oct': 0.1, 'Nov': 0.02, 'Dec': 0.03}
        prob = rain_map.get(self.month, 0.0)
        
        # Apply multiplier if custom
        if self.custom_params and 'rain_multiplier' in self.custom_params:
            prob *= self.custom_params['rain_multiplier']
            prob = min(1.0, prob)
        
        if random.random() < prob:
            self.days_since_rain = 0
            return True
        else:
            self.days_since_rain += 1
            return False

    def apply_rain_washout(self):
        if self.days_since_rain == 0:
            multiplier = 0.3
        elif self.days_since_rain == 1:
            multiplier = 0.7
        elif self.days_since_rain == 2:
            multiplier = 0.8
        else:
            multiplier = 1.0

        for agent in self.agents:
            if hasattr(agent, 'pm25_concentration'):
                agent.pm25_concentration *= multiplier

    def get_weekly_emission_multiplier(self, zone):
        if self.day_of_week in ['Sunday']:
            if zone.zone_type == 'industrial_core': return 0.8 
            elif zone.zone_type == 'vip': return 0.8
            elif zone.zone_type == 'residential_dense': return 0.9
            else: return 0.7
        return 1.0 

    # Helpers
    def get_day_of_week(self, day):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[(day - 1) % 7]
    
    def next_month(self, m):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        idx = months.index(m)
        return months[(idx + 1) % 12]

    def get_distance(self, loc1, loc2):
        d_lat = (loc1['lat'] - loc2['lat']) * 111
        d_lon = (loc1['lon'] - loc2['lon']) * 96
        return math.sqrt(d_lat**2 + d_lon**2)

    def get_bearing(self, loc1, loc2):
        d_lon = (loc2['lon'] - loc1['lon'])
        d_lat = (loc2['lat'] - loc1['lat'])
        angle = math.degrees(math.atan2(d_lon, d_lat))
        return (angle + 360) % 360
    
if __name__ == "__main__":
    model = DelhiAirshed(start_month="Nov", start_day=1)
    
    for day in range(30):
        model.step()
        if day % 5 == 0:
            print(f"Day {model.current_day}: Wind {model.regional_wind_speed:.1f} km/h")

    print("\n--- ZONE-WISE RESULTS ---")
    for agent in model.agents:
        print(f"{agent.name:15} | PM2.5: {agent.pm25_concentration:.2f} µg/m³")