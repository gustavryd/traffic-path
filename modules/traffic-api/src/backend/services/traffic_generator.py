import asyncio
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4
import math

class TrafficGenerator:
    """Traffic generation service that simulates dynamic traffic patterns on a graph network."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = {
            'node_count': config.get('node_count', 20) if config else 20,
            'update_interval': config.get('update_interval', 30000) if config else 30000,  # ms
            'base_traffic_level': config.get('base_traffic_level', 0.15) if config else 0.15,
            'traffic_variability': config.get('traffic_variability', 0.35) if config else 0.35,
            'incident_probability': config.get('incident_probability', 0.00001) if config else 0.00001,
            'road_density': config.get('road_density', 0.3) if config else 0.3
        }
        
        self.vertices: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.incidents: List[Dict[str, Any]] = []
        self.update_task: Optional[asyncio.Task] = None
        self.start_time = time.time()
        self.update_count = 0
        self.callbacks: List[callable] = []
        
        self._initialize_graph()
    
    def _initialize_graph(self):
        """Initialize the graph structure with vertices and edges."""
        # Create vertices (intersections/nodes)
        self.vertices = []
        for i in range(self.config['node_count']):
            self.vertices.append({
                'id': f'node_{i}',
                'name': f'Intersection {i + 1}',
                'x': random.random() * 800 + 50,
                'y': random.random() * 500 + 50
            })
        
        # Create edges (roads between nodes)
        self.edges = []
        edge_set = set()
        
        # Connect each node to a few random nearby nodes
        for i in range(len(self.vertices)):
            node_a = self.vertices[i]
            
            # Calculate distances to other nodes
            distances = []
            for j, node_b in enumerate(self.vertices):
                if i == j:
                    distances.append({'index': j, 'distance': float('inf')})
                else:
                    dx = node_a['x'] - node_b['x']
                    dy = node_a['y'] - node_b['y']
                    distances.append({'index': j, 'distance': math.sqrt(dx * dx + dy * dy)})
            
            # Sort by distance
            distances.sort(key=lambda x: x['distance'])
            
            # Connect to 2-4 nearest neighbors
            connect_count = 2 + random.randint(0, 2)
            for k in range(min(connect_count, len(distances))):
                j = distances[k]['index']
                edge_id = '-'.join(map(str, sorted([i, j])))
                
                if edge_id not in edge_set and random.random() < (self.config['road_density'] + 0.5):
                    edge_set.add(edge_id)
                    
                    distance = distances[k]['distance']
                    traffic = self._generate_random_traffic()
                    self.edges.append({
                        'id': f'edge_{len(self.edges)}',
                        'from': node_a['id'],
                        'to': self.vertices[j]['id'],
                        'weight': traffic,
                        'distance': round(distance / 10),
                        'speed': self._calculate_speed(traffic),
                        'vehicleCount': random.randint(0, 49),
                        'isIncident': False,
                        'incidentSeverity': 0,
                        'bidirectional': True
                    })
        
        # Ensure graph connectivity
        self._ensure_connectivity()
    
    def _ensure_connectivity(self):
        """Ensure all nodes are connected to at least one other node."""
        connected_nodes = set()
        
        for edge in self.edges:
            connected_nodes.add(edge['from'])
            connected_nodes.add(edge['to'])
        
        # Connect isolated nodes
        for vertex in self.vertices:
            if vertex['id'] not in connected_nodes:
                # Find nearest connected node
                nearest = None
                min_dist = float('inf')
                
                for other in self.vertices:
                    if other['id'] in connected_nodes:
                        dx = vertex['x'] - other['x']
                        dy = vertex['y'] - other['y']
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist < min_dist:
                            min_dist = dist
                            nearest = other
                
                if nearest:
                    traffic = self._generate_random_traffic()
                    self.edges.append({
                        'id': f'edge_{len(self.edges)}',
                        'from': vertex['id'],
                        'to': nearest['id'],
                        'weight': traffic,
                        'distance': round(min_dist / 10),
                        'speed': self._calculate_speed(traffic),
                        'vehicleCount': random.randint(0, 49),
                        'isIncident': False,
                        'incidentSeverity': 0,
                        'bidirectional': True
                    })
                    connected_nodes.add(vertex['id'])
    
    def _generate_random_traffic(self) -> float:
        """Generate random traffic level."""
        base = self.config['base_traffic_level']
        variability = self.config['traffic_variability']
        random_factor = (random.random() - 0.5) * variability * 4
        return max(0.0, min(1.0, base + random_factor))
    
    def _calculate_speed(self, traffic_level: float) -> int:
        """Calculate speed based on traffic level."""
        return round(60 - (traffic_level * 55))
    
    async def _update_traffic(self):
        """Update traffic state for all edges."""
        self.update_count += 1
        
        # Time-based patterns (rush hour simulation)
        hour = datetime.now().hour
        time_multiplier = 1.0
        
        if 7 <= hour <= 9:  # Morning rush
            time_multiplier = 1.5
        elif 17 <= hour <= 19:  # Evening rush
            time_multiplier = 1.6
        elif hour >= 23 or hour <= 5:  # Night time
            time_multiplier = 0.4
        
        # Update each edge
        for edge in self.edges:
            avg_neighbor_traffic = self._get_average_neighbor_traffic(edge)
            
            random_change = (random.random() - 0.5) * 0.2
            new_traffic = edge['weight'] * 0.85 + avg_neighbor_traffic * 0.05 + random_change
            
            # Occasional minor adjustments
            if random.random() < 0.05:
                new_traffic += (random.random() - 0.5) * 0.15
            
            # Apply time multiplier
            new_traffic *= time_multiplier
            
            # Clamp between 0 and 1
            new_traffic = max(0.0, min(1.0, new_traffic))
            
            edge['weight'] = new_traffic
            edge['speed'] = self._calculate_speed(new_traffic)
            
            # Update vehicle count
            base_vehicles = int(new_traffic * 100)
            edge['vehicleCount'] = max(0, base_vehicles + random.randint(-5, 5))
            
            # Random incident generation
            if not edge['isIncident'] and random.random() < self.config['incident_probability']:
                self.create_incident(
                    edge['id'],
                    random.random() * 0.5 + 0.3,
                    30000 + random.random() * 60000
                )
        
        # Update incidents
        self._update_incidents()
        
        # Notify callbacks
        await self._emit_update()
    
    def _get_average_neighbor_traffic(self, edge: Dict[str, Any]) -> float:
        """Get average traffic of connected edges."""
        connected_edges = [
            e for e in self.edges
            if e['id'] != edge['id'] and (
                e['from'] == edge['from'] or e['from'] == edge['to'] or
                e['to'] == edge['from'] or e['to'] == edge['to']
            )
        ]
        
        if not connected_edges:
            return self.config['base_traffic_level']
        
        total_traffic = sum(e['weight'] for e in connected_edges)
        return total_traffic / len(connected_edges)
    
    def create_incident(
        self,
        edge_id: str,
        severity: float = 0.5,
        duration: float = 60000,
        incident_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a traffic incident on an edge."""
        edge = next((e for e in self.edges if e['id'] == edge_id), None)
        
        if not edge:
            raise ValueError(f'Edge not found: {edge_id}')
        
        if edge['isIncident']:
            raise ValueError(f'Edge {edge_id} already has an active incident')
        
        # Validate severity and duration
        validated_severity = max(0.0, min(1.0, severity))
        validated_duration = max(10000, min(3600000, duration))
        
        incident = {
            'id': f'incident_{int(time.time() * 1000)}_{uuid4().hex[:9]}',
            'edgeId': edge_id,
            'from': edge['from'],
            'to': edge['to'],
            'severity': validated_severity,
            'startTime': int(time.time() * 1000),
            'endTime': int(time.time() * 1000) + int(validated_duration),
            'type': incident_type or self._get_random_incident_type(),
            'description': self._get_incident_description(
                incident_type or self._get_random_incident_type(),
                validated_severity
            )
        }
        
        self.incidents.append(incident)
        
        edge['isIncident'] = True
        edge['incidentSeverity'] = incident['severity']
        
        # Apply incident effect
        self._apply_incident_effect(edge_id, incident['severity'])
        
        return incident
    
    def _get_random_incident_type(self) -> str:
        """Get a random incident type."""
        types = ['accident', 'construction', 'roadblock', 'weather', 'event']
        return random.choice(types)
    
    def _get_incident_description(self, incident_type: str, severity: float) -> str:
        """Get incident description based on type and severity."""
        severity_text = 'severe' if severity > 0.7 else 'moderate' if severity > 0.4 else 'minor'
        severity_cap = severity_text.capitalize()
        
        descriptions = {
            'accident': f'{severity_cap} vehicle accident causing delays',
            'construction': f'{severity_cap} road construction work',
            'roadblock': f'{severity_cap} road closure or blockage',
            'weather': f'{severity_cap} weather-related conditions',
            'event': f'{severity_cap} special event causing congestion'
        }
        return descriptions.get(incident_type, f'{severity_cap} traffic incident')
    
    def _apply_incident_effect(self, edge_id: str, severity: float):
        """Apply traffic increase due to incident."""
        edge = next((e for e in self.edges if e['id'] == edge_id), None)
        if not edge:
            return
        
        # Increase traffic on incident road
        edge['weight'] = min(1.0, edge['weight'] + severity * 0.8)
        
        # Increase traffic on connected roads
        connected_edges = [
            e for e in self.edges
            if e['id'] != edge['id'] and (
                e['from'] == edge['from'] or e['from'] == edge['to'] or
                e['to'] == edge['from'] or e['to'] == edge['to']
            )
        ]
        
        for connected_edge in connected_edges:
            connected_edge['weight'] = min(1.0, connected_edge['weight'] + severity * 0.5)
    
    def _update_incidents(self):
        """Update and clear expired incidents."""
        now = int(time.time() * 1000)
        incidents_to_remove = []
        
        for incident in self.incidents:
            if now >= incident['endTime']:
                edge = next((e for e in self.edges if e['id'] == incident['edgeId']), None)
                if edge:
                    edge['isIncident'] = False
                    edge['incidentSeverity'] = 0
                incidents_to_remove.append(incident)
        
        for incident in incidents_to_remove:
            self.incidents.remove(incident)
    
    def clear_incident(self, incident_id: str) -> Dict[str, Any]:
        """Manually clear a specific incident."""
        incident = next((i for i in self.incidents if i['id'] == incident_id), None)
        
        if not incident:
            raise ValueError(f'Incident not found: {incident_id}')
        
        edge = next((e for e in self.edges if e['id'] == incident['edgeId']), None)
        if edge:
            edge['isIncident'] = False
            edge['incidentSeverity'] = 0
        
        self.incidents.remove(incident)
        return incident
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current state of the traffic system."""
        return {
            'vertices': self.vertices,
            'edges': [
                {
                    'id': e['id'],
                    'from': e['from'],
                    'to': e['to'],
                    'weight': e['weight'],
                    'distance': e['distance'],
                    'speed': e['speed'],
                    'vehicleCount': e['vehicleCount'],
                    'isIncident': e['isIncident'],
                    'incidentSeverity': e['incidentSeverity'],
                    'bidirectional': e['bidirectional']
                }
                for e in self.edges
            ],
            'incidents': self.incidents,
            'config': self.config,
            'updateCount': self.update_count,
            'timestamp': int(time.time() * 1000)
        }
    
    def get_edge_data(self, edge_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific edge."""
        return next((e for e in self.edges if e['id'] == edge_id), None)
    
    def get_vertex_data(self, vertex_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific vertex."""
        return next((v for v in self.vertices if v['id'] == vertex_id), None)
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Get all edges with basic info."""
        return [
            {
                'id': e['id'],
                'from': e['from'],
                'to': e['to'],
                'distance': e['distance'],
                'currentWeight': e['weight'],
                'hasIncident': e['isIncident']
            }
            for e in self.edges
        ]
    
    def get_available_edges_for_incident(self) -> List[Dict[str, Any]]:
        """Get edges available for incident creation."""
        return [
            {
                'id': e['id'],
                'from': e['from'],
                'to': e['to'],
                'distance': e['distance'],
                'currentTraffic': e['weight']
            }
            for e in self.edges if not e['isIncident']
        ]
    
    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Get all active incidents."""
        now = int(time.time() * 1000)
        return [
            {
                **i,
                'remainingTime': max(0, i['endTime'] - now)
            }
            for i in self.incidents
        ]
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration."""
        needs_reinit = False
        
        if 'node_count' in new_config and new_config['node_count'] != self.config['node_count']:
            self.config['node_count'] = new_config['node_count']
            needs_reinit = True
        
        if 'road_density' in new_config:
            self.config['road_density'] = new_config['road_density']
            needs_reinit = True
        
        if needs_reinit:
            self._initialize_graph()
        
        if 'update_interval' in new_config:
            self.config['update_interval'] = new_config['update_interval']
        
        if 'base_traffic_level' in new_config:
            self.config['base_traffic_level'] = new_config['base_traffic_level']
        
        if 'traffic_variability' in new_config:
            self.config['traffic_variability'] = new_config['traffic_variability']
        
        if 'incident_probability' in new_config:
            self.config['incident_probability'] = new_config['incident_probability']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get traffic statistics."""
        total_edges = len(self.edges)
        total_vertices = len(self.vertices)
        total_traffic = sum(e['weight'] for e in self.edges)
        total_vehicles = sum(e['vehicleCount'] for e in self.edges)
        avg_speed = sum(e['speed'] for e in self.edges)
        
        return {
            'totalVertices': total_vertices,
            'totalEdges': total_edges,
            'averageTrafficLevel': f"{(total_traffic / total_edges):.3f}" if total_edges > 0 else "0.000",
            'totalVehicles': total_vehicles,
            'averageSpeed': round(avg_speed / total_edges) if total_edges > 0 else 0,
            'activeIncidents': len(self.incidents),
            'updateCount': self.update_count,
            'uptime': int((time.time() - self.start_time) * 1000)
        }
    
    def on_update(self, callback: callable):
        """Register a callback for traffic updates."""
        self.callbacks.append(callback)
    
    async def _emit_update(self):
        """Emit update to all registered callbacks."""
        state = self.get_current_state()
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(state)
                else:
                    callback(state)
            except Exception as e:
                print(f"Error in update callback: {e}")
    
    async def start(self):
        """Start the traffic generator."""
        if self.update_task and not self.update_task.done():
            print('Traffic generator already running')
            return
        
        print('Starting traffic generator...')
        
        async def update_loop():
            while True:
                await self._update_traffic()
                await asyncio.sleep(self.config['update_interval'] / 1000)
        
        self.update_task = asyncio.create_task(update_loop())
    
    async def stop(self):
        """Stop the traffic generator."""
        if self.update_task and not self.update_task.done():
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
            self.update_task = None
            print('Traffic generator stopped')
