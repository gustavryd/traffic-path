const express = require('express');
const WebSocket = require('ws');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const TrafficGenerator = require('./trafficGenerator');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Create HTTP server
const server = app.listen(PORT, () => {
  console.log(`Traffic Data API server running on port ${PORT}`);
  console.log(`WebSocket available at ws://localhost:${PORT}`);
  console.log(`REST API available at http://localhost:${PORT}`);
});

// Create WebSocket server
const wss = new WebSocket.Server({ server });

// Initialize traffic generator with graph structure
const trafficGenerator = new TrafficGenerator({
  nodeCount: 20,
  roadDensity: 0.3,
  updateInterval: 5000
});

// WebSocket connection handling
wss.on('connection', (ws) => {
  const clientId = uuidv4();
  console.log(`Client ${clientId} connected`);

  // Send initial traffic state
  ws.send(JSON.stringify({
    type: 'initial',
    data: trafficGenerator.getCurrentState()
  }));

  // Handle client messages
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      if (data.type === 'subscribe') {
        console.log(`Client ${clientId} subscribed to traffic updates`);
      } else if (data.type === 'configure') {
        trafficGenerator.updateConfig(data.config);
        console.log(`Client ${clientId} updated configuration`);
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  });

  ws.on('close', () => {
    console.log(`Client ${clientId} disconnected`);
  });
});

// Broadcast traffic updates to all connected clients
trafficGenerator.on('update', (trafficData) => {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({
        type: 'update',
        data: trafficData,
        timestamp: Date.now()
      }));
    }
  });
});

// REST API Endpoints

// Get current traffic state (graph structure)
app.get('/api/traffic/current', (req, res) => {
  res.json({
    success: true,
    data: trafficGenerator.getCurrentState()
  });
});

// Get graph data in specific format
app.get('/api/traffic/graph', (req, res) => {
  const state = trafficGenerator.getCurrentState();
  res.json({
    success: true,
    data: {
      vertices: state.vertices,
      edges: state.edges
    }
  });
});

// Get specific vertex data
app.get('/api/traffic/vertex/:id', (req, res) => {
  const vertexData = trafficGenerator.getVertexData(req.params.id);
  
  if (vertexData) {
    res.json({
      success: true,
      data: vertexData
    });
  } else {
    res.status(404).json({
      success: false,
      error: 'Vertex not found'
    });
  }
});

// Get specific edge data
app.get('/api/traffic/edge/:id', (req, res) => {
  const edgeData = trafficGenerator.getEdgeData(req.params.id);
  
  if (edgeData) {
    res.json({
      success: true,
      data: edgeData
    });
  } else {
    res.status(404).json({
      success: false,
      error: 'Edge not found'
    });
  }
});

// Get configuration
app.get('/api/config', (req, res) => {
  res.json({
    success: true,
    data: trafficGenerator.getConfig()
  });
});

// Update configuration
app.post('/api/config', (req, res) => {
  try {
    trafficGenerator.updateConfig(req.body);
    res.json({
      success: true,
      data: trafficGenerator.getConfig()
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

// Get traffic statistics
app.get('/api/traffic/stats', (req, res) => {
  res.json({
    success: true,
    data: trafficGenerator.getStats()
  });
});

// Get all edges (roads)
app.get('/api/traffic/edges', (req, res) => {
  try {
    const edges = trafficGenerator.getAllEdges();
    res.json({
      success: true,
      data: edges
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get available edges for incident creation (edges without active incidents)
app.get('/api/traffic/edges/available', (req, res) => {
  try {
    const availableEdges = trafficGenerator.getAvailableEdgesForIncident();
    res.json({
      success: true,
      data: availableEdges,
      count: availableEdges.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get all active incidents
app.get('/api/traffic/incidents', (req, res) => {
  try {
    const incidents = trafficGenerator.getActiveIncidents();
    res.json({
      success: true,
      data: incidents,
      count: incidents.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Create traffic incident on an edge (road)
app.post('/api/traffic/incident', (req, res) => {
  const { edgeId, severity, duration, type } = req.body;
  
  // Validate required parameter
  if (!edgeId) {
    return res.status(400).json({
      success: false,
      error: 'edgeId is required'
    });
  }
  
  try {
    const incident = trafficGenerator.createIncident(
      edgeId, 
      severity || 0.5, 
      duration || 60000,
      type || null
    );
    res.json({
      success: true,
      message: 'Incident created successfully',
      data: incident
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

// Clear a specific incident manually
app.delete('/api/traffic/incident/:incidentId', (req, res) => {
  const { incidentId } = req.params;
  
  try {
    const clearedIncident = trafficGenerator.clearIncident(incidentId);
    res.json({
      success: true,
      message: 'Incident cleared successfully',
      data: clearedIncident
    });
  } catch (error) {
    res.status(404).json({
      success: false,
      error: error.message
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    timestamp: Date.now()
  });
});

// Start traffic generation
trafficGenerator.start();

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  trafficGenerator.stop();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
