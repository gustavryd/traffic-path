const EventEmitter = require('events');

class TrafficGenerator extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      nodeCount: config.nodeCount || 20,
      updateInterval: config.updateInterval || 30000, // Changed from 5000 to 15000ms (update every 15 seconds)
      baseTrafficLevel: config.baseTrafficLevel || 0.15,
      trafficVariability: config.trafficVariability || 0.35, // Changed from 0.05 to 0.35 (higher variability)
      incidentProbability: config.incidentProbability || 0.00001,
      roadDensity: config.roadDensity || 0.3 // Probability of connection between nodes
    };
    
    this.vertices = [];
    this.edges = [];
    this.incidents = [];
    this.updateTimer = null;
    this.startTime = Date.now();
    this.updateCount = 0;
    
    this.initializeGraph();
  }
  
  initializeGraph() {
    // Create vertices (intersections/nodes)
    this.vertices = [];
    for (let i = 0; i < this.config.nodeCount; i++) {
      this.vertices.push({
        id: `node_${i}`,
        name: `Intersection ${i + 1}`,
        x: Math.random() * 800 + 50, // For visualization positioning
        y: Math.random() * 500 + 50
      });
    }
    
    // Create edges (roads between nodes)
    this.edges = [];
    const edgeSet = new Set();
    
    // Connect each node to a few random nearby nodes
    for (let i = 0; i < this.vertices.length; i++) {
      const nodeA = this.vertices[i];
      
      // Calculate distances to other nodes
      const distances = this.vertices.map((nodeB, j) => {
        if (i === j) return { index: j, distance: Infinity };
        const dx = nodeA.x - nodeB.x;
        const dy = nodeA.y - nodeB.y;
        return { index: j, distance: Math.sqrt(dx * dx + dy * dy) };
      });
      
      // Sort by distance
      distances.sort((a, b) => a.distance - b.distance);
      
      // Connect to 2-4 nearest neighbors
      const connectCount = 2 + Math.floor(Math.random() * 3);
      for (let k = 0; k < Math.min(connectCount, distances.length); k++) {
        const j = distances[k].index;
        const edgeId = [i, j].sort().join('-');
        
        if (!edgeSet.has(edgeId) && Math.random() < (this.config.roadDensity + 0.5)) {
          edgeSet.add(edgeId);
          
          const distance = distances[k].distance;
          this.edges.push({
            id: `edge_${this.edges.length}`,
            from: nodeA.id,
            to: this.vertices[j].id,
            weight: this.generateRandomTraffic(),
            distance: Math.round(distance / 10), // Scale to reasonable values
            speed: this.calculateSpeed(this.config.baseTrafficLevel),
            vehicleCount: Math.floor(Math.random() * 50),
            isIncident: false,
            incidentSeverity: 0,
            bidirectional: true
          });
        }
      }
    }
    
    // Ensure graph is connected (at least one path between any two nodes)
    this.ensureConnectivity();
  }
  
  ensureConnectivity() {
    // Simple connectivity check - ensure every node has at least one edge
    const connectedNodes = new Set();
    
    for (const edge of this.edges) {
      connectedNodes.add(edge.from);
      connectedNodes.add(edge.to);
    }
    
    // Connect isolated nodes to nearest connected node
    for (const vertex of this.vertices) {
      if (!connectedNodes.has(vertex.id)) {
        // Find nearest connected node
        let nearest = null;
        let minDist = Infinity;
        
        for (const other of this.vertices) {
          if (connectedNodes.has(other.id)) {
            const dx = vertex.x - other.x;
            const dy = vertex.y - other.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < minDist) {
              minDist = dist;
              nearest = other;
            }
          }
        }
        
        if (nearest) {
          this.edges.push({
            id: `edge_${this.edges.length}`,
            from: vertex.id,
            to: nearest.id,
            weight: this.generateRandomTraffic(),
            distance: Math.round(minDist / 10),
            speed: this.calculateSpeed(this.config.baseTrafficLevel),
            vehicleCount: Math.floor(Math.random() * 50),
            isIncident: false,
            incidentSeverity: 0,
            bidirectional: true
          });
          connectedNodes.add(vertex.id);
        }
      }
    }
  }
  
  generateRandomTraffic() {
    const base = this.config.baseTrafficLevel;
    const variability = this.config.trafficVariability;
    // Generate more diverse initial traffic levels with wider spread
    const randomFactor = (Math.random() - 0.5) * variability * 4; // Increased from *2 to *4
    return Math.max(0, Math.min(1, base + randomFactor));
  }
  
  calculateSpeed(trafficLevel) {
    // Speed inversely proportional to traffic level
    // 0 traffic = 60 mph, high traffic = 5 mph
    return Math.round(60 - (trafficLevel * 55));
  }
  
  updateTraffic() {
    this.updateCount++;
    
    // Apply time-based patterns (rush hour simulation)
    const hour = new Date().getHours();
    let timeMultiplier = 1.0;
    
    // Morning rush: 7-9 AM
    if (hour >= 7 && hour <= 9) {
      timeMultiplier = 1.5;
    }
    // Evening rush: 5-7 PM
    else if (hour >= 17 && hour <= 19) {
      timeMultiplier = 1.6;
    }
    // Night time: 11 PM - 5 AM
    else if (hour >= 23 || hour <= 5) {
      timeMultiplier = 0.4;
    }
    
    // Update each edge (road)
    for (const edge of this.edges) {
      // Get connected edges for traffic flow simulation
      const avgNeighborTraffic = this.getAverageNeighborTraffic(edge);
      
      // Slower, more gradual changes
      // High current traffic influence (0.85) for stability and slow transitions
      // Low neighbor influence (0.05) to maintain road independence
      // Small random factor (0.1) for gentle variations
      let randomChange = (Math.random() - 0.5) * 0.2; // -0.1 to +0.1 gentle swing
      let newTraffic = edge.weight * 0.85 + avgNeighborTraffic * 0.05 + randomChange;
      
      // Occasional minor traffic adjustments (5% chance)
      if (Math.random() < 0.05) {
        newTraffic += (Math.random() - 0.5) * 0.15; // Small ±0.075 adjustment
      }
      
      // Apply time multiplier
      newTraffic *= timeMultiplier;
      
      // Clamp between 0 and 1
      newTraffic = Math.max(0, Math.min(1, newTraffic));
      
      edge.weight = newTraffic;
      edge.speed = this.calculateSpeed(newTraffic);
      
      // Update vehicle count based on traffic level with moderate variability
      const baseVehicles = Math.floor(newTraffic * 100);
      edge.vehicleCount = baseVehicles + Math.floor(Math.random() * 10 - 5); // Reduced to ±5 vehicles
      edge.vehicleCount = Math.max(0, edge.vehicleCount);
      
      // Random incident generation on roads
      if (!edge.isIncident && Math.random() < this.config.incidentProbability) {
        this.createIncident(edge.id, Math.random() * 0.5 + 0.3, 30000 + Math.random() * 60000);
      }
    }
    
    // Update incidents
    this.updateIncidents();
    
    // Emit update event
    this.emit('update', this.getCurrentState());
  }
  
  getAverageNeighborTraffic(edge) {
    // Find edges connected to the same nodes
    const connectedEdges = this.edges.filter(e => 
      e.id !== edge.id && (
        e.from === edge.from || e.from === edge.to ||
        e.to === edge.from || e.to === edge.to
      )
    );
    
    if (connectedEdges.length === 0) {
      return this.config.baseTrafficLevel;
    }
    
    const totalTraffic = connectedEdges.reduce((sum, e) => sum + e.weight, 0);
    return totalTraffic / connectedEdges.length;
  }
  
  createIncident(edgeId, severity = 0.5, duration = 60000, incidentType = null) {
    const edge = this.edges.find(e => e.id === edgeId);
    
    if (!edge) {
      throw new Error(`Edge not found: ${edgeId}`);
    }
    
    // Check if edge already has an incident
    if (edge.isIncident) {
      throw new Error(`Edge ${edgeId} already has an active incident`);
    }
    
    // Validate and clamp severity between 0 and 1
    const validatedSeverity = Math.max(0, Math.min(1, severity));
    
    // Validate duration (minimum 10 seconds, maximum 1 hour)
    const validatedDuration = Math.max(10000, Math.min(3600000, duration));
    
    const incident = {
      id: `incident_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      edgeId: edgeId,
      from: edge.from,
      to: edge.to,
      severity: validatedSeverity,
      startTime: Date.now(),
      endTime: Date.now() + validatedDuration,
      type: incidentType || this.getRandomIncidentType(),
      description: this.getIncidentDescription(incidentType || this.getRandomIncidentType(), validatedSeverity)
    };
    
    this.incidents.push(incident);
    
    edge.isIncident = true;
    edge.incidentSeverity = incident.severity;
    
    // Increase traffic on this road and connected roads
    this.applyIncidentEffect(edgeId, incident.severity);
    
    console.log(`Incident created on ${edgeId} (${edge.from} → ${edge.to}): ${incident.type} with severity ${validatedSeverity.toFixed(2)}`);
    
    // Emit incident created event
    this.emit('incidentCreated', incident);
    
    return incident;
  }
  
  getRandomIncidentType() {
    const types = ['accident', 'construction', 'roadblock', 'weather', 'event'];
    return types[Math.floor(Math.random() * types.length)];
  }
  
  getIncidentDescription(type, severity) {
    const severityText = severity > 0.7 ? 'severe' : severity > 0.4 ? 'moderate' : 'minor';
    const descriptions = {
      'accident': `${severityText.charAt(0).toUpperCase() + severityText.slice(1)} vehicle accident causing delays`,
      'construction': `${severityText.charAt(0).toUpperCase() + severityText.slice(1)} road construction work`,
      'roadblock': `${severityText.charAt(0).toUpperCase() + severityText.slice(1)} road closure or blockage`,
      'weather': `${severityText.charAt(0).toUpperCase() + severityText.slice(1)} weather-related conditions`,
      'event': `${severityText.charAt(0).toUpperCase() + severityText.slice(1)} special event causing congestion`
    };
    return descriptions[type] || `${severityText.charAt(0).toUpperCase() + severityText.slice(1)} traffic incident`;
  }
  
  getAllEdges() {
    return this.edges.map(e => ({
      id: e.id,
      from: e.from,
      to: e.to,
      distance: e.distance,
      currentWeight: e.weight,
      hasIncident: e.isIncident
    }));
  }
  
  getAvailableEdgesForIncident() {
    return this.edges
      .filter(e => !e.isIncident)
      .map(e => ({
        id: e.id,
        from: e.from,
        to: e.to,
        distance: e.distance,
        currentTraffic: e.weight
      }));
  }
  
  clearIncident(incidentId) {
    const incident = this.incidents.find(i => i.id === incidentId);
    
    if (!incident) {
      throw new Error(`Incident not found: ${incidentId}`);
    }
    
    const edge = this.edges.find(e => e.id === incident.edgeId);
    if (edge) {
      edge.isIncident = false;
      edge.incidentSeverity = 0;
    }
    
    this.incidents = this.incidents.filter(i => i.id !== incidentId);
    
    console.log(`Incident ${incidentId} manually cleared from ${incident.edgeId}`);
    
    // Emit incident cleared event
    this.emit('incidentCleared', incident);
    
    return incident;
  }
  
  getActiveIncidents() {
    return this.incidents.map(i => ({
      ...i,
      remainingTime: Math.max(0, i.endTime - Date.now())
    }));
  }
  
  applyIncidentEffect(edgeId, severity) {
    const edge = this.edges.find(e => e.id === edgeId);
    if (!edge) return;
    
    // Higher traffic impact on incident road (0.5 -> 0.8)
    edge.weight = Math.min(1, edge.weight + severity * 0.8);
    
    // Higher impact on connected roads (0.3 -> 0.5)
    const connectedEdges = this.edges.filter(e => 
      e.id !== edge.id && (
        e.from === edge.from || e.from === edge.to ||
        e.to === edge.from || e.to === edge.to
      )
    );
    
    for (const connectedEdge of connectedEdges) {
      connectedEdge.weight = Math.min(1, connectedEdge.weight + severity * 0.5);
    }
  }
  
  updateIncidents() {
    const now = Date.now();
    this.incidents = this.incidents.filter(incident => {
      if (now >= incident.endTime) {
        // Clear incident from edge
        const edge = this.edges.find(e => e.id === incident.edgeId);
        if (edge) {
          edge.isIncident = false;
          edge.incidentSeverity = 0;
        }
        console.log(`Incident cleared on ${incident.edgeId}`);
        return false;
      }
      return true;
    });
  }
  
  getCurrentState() {
    return {
      vertices: this.vertices,
      edges: this.edges.map(e => ({
        id: e.id,
        from: e.from,
        to: e.to,
        weight: e.weight,
        distance: e.distance,
        speed: e.speed,
        vehicleCount: e.vehicleCount,
        isIncident: e.isIncident,
        incidentSeverity: e.incidentSeverity,
        bidirectional: e.bidirectional
      })),
      incidents: this.incidents,
      config: this.config,
      updateCount: this.updateCount,
      timestamp: Date.now()
    };
  }
  
  getEdgeData(edgeId) {
    return this.edges.find(e => e.id === edgeId) || null;
  }
  
  getVertexData(vertexId) {
    return this.vertices.find(v => v.id === vertexId) || null;
  }
  
  getConfig() {
    return { ...this.config };
  }
  
  updateConfig(newConfig) {
    let needsReinit = false;
    
    if (newConfig.nodeCount && newConfig.nodeCount !== this.config.nodeCount) {
      this.config.nodeCount = newConfig.nodeCount;
      needsReinit = true;
    }
    if (newConfig.roadDensity !== undefined) {
      this.config.roadDensity = newConfig.roadDensity;
      needsReinit = true;
    }
    
    if (needsReinit) {
      this.initializeGraph();
    }
    
    if (newConfig.updateInterval) {
      this.config.updateInterval = newConfig.updateInterval;
      if (this.updateTimer) {
        this.stop();
        this.start();
      }
    }
    if (newConfig.baseTrafficLevel !== undefined) {
      this.config.baseTrafficLevel = newConfig.baseTrafficLevel;
    }
    if (newConfig.trafficVariability !== undefined) {
      this.config.trafficVariability = newConfig.trafficVariability;
    }
    if (newConfig.incidentProbability !== undefined) {
      this.config.incidentProbability = newConfig.incidentProbability;
    }
  }
  
  getStats() {
    const totalEdges = this.edges.length;
    const totalVertices = this.vertices.length;
    let totalTraffic = 0;
    let totalVehicles = 0;
    let avgSpeed = 0;
    
    for (const edge of this.edges) {
      totalTraffic += edge.weight;
      totalVehicles += edge.vehicleCount;
      avgSpeed += edge.speed;
    }
    
    return {
      totalVertices,
      totalEdges,
      averageTrafficLevel: (totalTraffic / totalEdges).toFixed(3),
      totalVehicles,
      averageSpeed: Math.round(avgSpeed / totalEdges),
      activeIncidents: this.incidents.length,
      updateCount: this.updateCount,
      uptime: Date.now() - this.startTime
    };
  }
  
  start() {
    if (this.updateTimer) {
      console.log('Traffic generator already running');
      return;
    }
    
    console.log('Starting traffic generator...');
    this.updateTimer = setInterval(() => {
      this.updateTraffic();
    }, this.config.updateInterval);
  }
  
  stop() {
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
      this.updateTimer = null;
      console.log('Traffic generator stopped');
    }
  }
}

module.exports = TrafficGenerator;
