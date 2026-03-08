from mesa import Agent
import math

class PollutionHub(Agent):
    """
    A specific location in Delhi simulating Daily Pollution Load.
    Reads custom parameters from model.custom_params if provided.
    """
    def __init__(self, unique_id, model, name, vehicle_data, congestion_level, 
                 road_silt, dist_to_industry, garbage_fires, const_sites, 
                 zone_type, location):
        super().__init__(model)
        self.unique_id = unique_id
        self.name = name
        
        # Configuration
        self.vehicle_data = vehicle_data 
        self.congestion_factor = congestion_level 
        self.road_silt_factor = road_silt
        self.dist_to_industry = dist_to_industry
        self.garbage_fire_count = garbage_fires
        self.construction_sites = const_sites
        self.zone_type = zone_type
        self.location = location

        # Dynamic State
        self.mixing_height = 500
        self.wind_speed = 3.0
        self.wind_dir = 'NW'
        self.is_foggy = False
        self.emission_multiplier = 1.0
        self.external_load_kg = 0.0
        
        # Outputs
        self.pm25_concentration = 100.0
        self.generated_load_kg = 0.0
        self.breakdown = {}

    def step(self):
        """Calculate Total Pollution generated in 24 HOURS"""
        
        custom = self.model.custom_params
        
        # --- A. TRANSPORT MODULE ---
        # Emission factors (default or custom)
        if custom and 'emission_factors' in custom:
            ef_base = custom['emission_factors']
        else:
            ef_base = {'trucks': 30.0, 'buses': 12.0, 'cars': 2.0, 'two_wheelers': 2.0, 'autos': 1.5}
        
        total_transport_emission_g = 0.0
        
        for v_type, data in self.vehicle_data.items():
            if v_type in ef_base:
                N = data['count']
                T = data['avg_stay_hrs']
                EF = ef_base[v_type]
                Alpha = self.congestion_factor 
                
                emission_g = (N * T) * EF * Alpha * self.emission_multiplier
                total_transport_emission_g += emission_g
        
        q_transport_kg = total_transport_emission_g / 1000.0

        # --- B. ROAD DUST MODULE ---
        avg_speed = 40.0 / self.congestion_factor 
        
        # Dust formula parameters (default or custom)
        if custom and 'dust_k' in custom:
            k = custom['dust_k']
            silt_exp = custom.get('dust_silt_exp', 0.91)
            weight_exp = custom.get('dust_weight_exp', 1.02)
        else:
            k = 0.15
            silt_exp = 0.91
            weight_exp = 1.02
        
        sL = self.road_silt_factor 
        
        vehicle_weights = {'trucks': 15.0, 'buses': 15.0, 'cars': 1.5, 'autos': 0.8, 'two_wheelers': 0.15}
        
        speed_turbulence = (avg_speed / 20.0)
        daily_dampness = 0.75 

        total_dust_g = 0.0
        for v_type, data in self.vehicle_data.items():
            if v_type in vehicle_weights:
                W = vehicle_weights[v_type]
                total_km = (data['count'] * data['avg_stay_hrs']) * avg_speed
                
                # AP-42 Formula with custom exponents
                ef_dust = k * (sL ** silt_exp) * (W ** weight_exp)
                total_dust_g += (total_km * ef_dust)

        q_dust_kg = (total_dust_g * speed_turbulence * daily_dampness) / 1000.0

        # --- C. INDUSTRIAL MODULE ---
        # Industrial loads (default or custom)
        if custom and 'industrial_loads' in custom:
            loads = custom['industrial_loads']
            ncr_clusters = [
                {"name": "Cluster_E", "load": loads.get('Cluster_E', 15000), "bearing": 90,  
                "dist": max(self.dist_to_industry, 5), "so2_pot": 0.2, "stack_height": 40},

                {"name": "Cluster_S", "load": loads.get('Cluster_S', 12000), "bearing": 180, 
                "dist": max(self.dist_to_industry + 10, 15), "so2_pot": 0.3, "stack_height": 30},

                {"name": "Cluster_NW", "load": loads.get('Cluster_NW', 45000), "bearing": 315, 
                "dist": 80, "so2_pot": 0.9, "stack_height": 120},

                {"name": "Cluster_Brick", "load": loads.get('Cluster_Brick', 25000), "bearing": 0, 
                "dist": 30, "so2_pot": 0.1, "stack_height": 10}
            ]
        else:
            ncr_clusters = [
                {"name": "Cluster_E", "load": 15000, "bearing": 90,  
                "dist": max(self.dist_to_industry, 5), "so2_pot": 0.2, "stack_height": 40},

                {"name": "Cluster_S", "load": 12000, "bearing": 180, 
                "dist": max(self.dist_to_industry + 10, 15), "so2_pot": 0.3, "stack_height": 30},

                {"name": "Cluster_NW", "load": 45000, "bearing": 315, 
                "dist": 80, "so2_pot": 0.9, "stack_height": 120},

                {"name": "Cluster_Brick", "load": 25000, "bearing": 0, 
                "dist": 30, "so2_pot": 0.1, "stack_height": 10}
            ]
                
        wind_map = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}
        curr_wind_deg = wind_map.get(self.wind_dir, 315)
        
        total_ind_kg = 0.0
        hub_width_km = 5.0
        
        for cluster in ncr_clusters:
            # Seasonality
            if cluster["name"] == "Cluster_Brick" and self.model.month in ["Jul", "Aug", "Sep"]:
                continue

            # Wind Alignment
            diff = abs(curr_wind_deg - cluster["bearing"])
            if diff > 180: diff = 360 - diff
            
            alpha_wind = 1.0 - (diff / 45.0) if diff <= 45 else 0.0
            if cluster["name"] == "Cluster_Brick": 
                alpha_wind = max(alpha_wind, 0.3)
            
            # Plume Dispersion
            plume_width = cluster["dist"] * 0.5
            capture_ratio = min(1.0, hub_width_km / max(plume_width, 1.0))
            
            # Chemistry
            chem_mult = 1.0 + (cluster["so2_pot"] * 1.5) if self.is_foggy else 1.0 + (cluster["so2_pot"] * 0.1)
            
            # Decay
            travel_time = cluster["dist"] / max(self.wind_speed, 1.0)
            decay = math.exp(-0.05 * travel_time)
    
            # Stack Height vs Mixing Height
            stack_h = cluster["stack_height"]
            
            if stack_h < self.mixing_height * 0.7:
                stack_factor = 1.0
            elif stack_h < self.mixing_height:
                stack_factor = 0.7
            else:
                stack_factor = 0.4
            
            total_ind_kg += (cluster["load"] * alpha_wind * capture_ratio 
                            * chem_mult * decay * stack_factor * self.emission_multiplier)
            
        q_industry_kg = total_ind_kg

        # --- D. GARBAGE BURNING ---
        if custom and 'garbage_emission' in custom:
            garbage_ef = custom['garbage_emission']
        else:
            garbage_ef = 300.0
        
        heat_mult = 1.5 if self.model.month in ["Nov", "Dec", "Jan", "Feb"] else 1.0
        q_garbage_kg = (self.garbage_fire_count * heat_mult * garbage_ef) / 1000.0

        # --- E. CONSTRUCTION ---
        if custom and 'construction_emission' in custom:
            const_ef = custom['construction_emission']
        else:
            const_ef = 2.0  # kg/site/day
        
        is_severe = (self.model.month in ["Nov", "Dec", "Jan"] and self.mixing_height < 400)
        activity = 0.2 if is_severe else 1.0
        
        q_construction_kg = (self.construction_sites * const_ef * activity)

        # --- F. SECONDARY AEROSOL ---
        # Secondary PM parameters (default or custom)
        if custom and 'nox_multiplier' in custom:
            nox_mult = custom['nox_multiplier']
            fog_conv = custom.get('fog_conversion', 0.15)
            clear_conv = custom.get('clear_conversion', 0.03)
        else:
            nox_mult = 6.0
            fog_conv = 0.15
            clear_conv = 0.03
        
        conversion_rate = fog_conv if self.is_foggy else clear_conv
        q_secondary_kg = (q_transport_kg * nox_mult) * conversion_rate

        # --- G. AGGREGATION & BOX MODEL ---
        self.generated_load_kg = (q_transport_kg + q_dust_kg + q_industry_kg + 
                                  q_garbage_kg + q_construction_kg + q_secondary_kg)
        
        total_local_input_kg = self.generated_load_kg + self.external_load_kg
        
        # Dilution Volume
        cross_section_m2 = 5000 * self.mixing_height
        wind_run_m = max(self.wind_speed, 0.5) * 1000 * 24
        ventilation_volume_m3 = cross_section_m2 * wind_run_m
        
        # LOCAL Concentration
        local_concentration = (total_local_input_kg * 1e9) / ventilation_volume_m3

        # --- H. REGIONAL STUBBLE BACKGROUND ---
        is_nw_wind = (self.wind_dir in ['NW', 'N', 'W'])

        if is_nw_wind and self.model.stubble_fire_count > 0:
            total_stubble_emission_kg = self.model.stubble_fire_count * 2200.0 * 0.7
            
            ncr_area_m2 = 55_000_000_000
            ncr_volume_m3 = ncr_area_m2 * self.mixing_height
            
            stubble_base = (total_stubble_emission_kg * 1e9) / ncr_volume_m3
            
            # Fumigation factor
            stubble_injection_height = 600
            
            if self.mixing_height >= stubble_injection_height:
                fumigation_factor = 1.0
            elif self.mixing_height >= 300:
                fumigation_factor = 0.3 + 0.7 * ((self.mixing_height - 300) / (stubble_injection_height - 300))
            else:
                fumigation_factor = 0.2
            
            # Position modifier
            position_weights = {
                'Bahadurgarh': 1.1,
                'Uttam Nagar': 0.9,
                'Lutyens Delhi': 1.0,
                'Anand Vihar': 0.85,
                'Okhla': 0.75
            }
            position_modifier = position_weights.get(self.name, 1.0)
            
            stubble_concentration = stubble_base * fumigation_factor * position_modifier

        else:
            stubble_concentration = 0.0
                
        # --- I. FINAL CONCENTRATION ---
        self.pm25_concentration = local_concentration + stubble_concentration
        
        # --- J. BREAKDOWN FOR VISUALIZATION ---
        self.breakdown = {
            "Transport": q_transport_kg,
            "Dust": q_dust_kg,
            "Industry": q_industry_kg,
            "Garbage": q_garbage_kg,
            "Construction": q_construction_kg,
            "Secondary": q_secondary_kg,
            "External_Inflow": self.external_load_kg,
            "Total_Local_Load_kg": total_local_input_kg,
            
            "Local_Concentration": local_concentration,
            "Stubble_Concentration": stubble_concentration,
            "Total_Concentration": self.pm25_concentration,
            
            "AQI_Conc": self.pm25_concentration
        }

    def advance(self):
        """Mesa 3.0+ compatibility"""
        pass