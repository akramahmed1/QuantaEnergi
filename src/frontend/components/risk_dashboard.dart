// AR Risk Dashboard Component
// Provides augmented reality visualizations for risk analytics and portfolio management

import 'package:flutter/material.dart';
import 'package:ar_flutter_plugin/ar_flutter_plugin.dart';
import 'package:ar_flutter_plugin/datatypes/config_planedetection.dart';
import 'package:ar_flutter_plugin/datatypes/node_types.dart';
import 'package:ar_flutter_plugin/managers/ar_location_manager.dart';
import 'package:ar_flutter_plugin/managers/ar_session_manager.dart';
import 'package:ar_flutter_plugin/managers/ar_object_manager.dart';
import 'package:ar_flutter_plugin/managers/ar_anchor_manager.dart';
import 'package:ar_flutter_plugin/models/ar_anchor.dart';
import 'package:ar_flutter_plugin/models/ar_node.dart';
import 'package:ar_flutter_plugin/models/ar_hittest_result.dart';
import 'dart:async';
import 'dart:math';
import 'dart:ui';

class ARRiskDashboard extends StatefulWidget {
  final Map<String, dynamic>? riskData;
  final Function(String)? onRiskAlert;
  final Function(Map<String, dynamic>)? onPortfolioUpdate;

  const ARRiskDashboard({
    Key? key,
    this.riskData,
    this.onRiskAlert,
    this.onPortfolioUpdate,
  }) : super(key: key);

  @override
  _ARRiskDashboardState createState() => _ARRiskDashboardState();
}

class _ARRiskDashboardState extends State<ARRiskDashboard>
    with TickerProviderStateMixin {
  // AR Controllers
  late ARSessionManager arSessionManager;
  late ARObjectManager arObjectManager;
  late ARAnchorManager arAnchorManager;
  late ARLocationManager arLocationManager;

  // State variables
  bool isARInitialized = false;
  bool isDashboardVisible = false;
  String selectedView = 'overview';
  
  // Risk data
  Map<String, dynamic> riskMetrics = {
    'var_95': 125000,
    'var_99': 185000,
    'max_drawdown': 8.5,
    'sharpe_ratio': 1.85,
    'beta': 0.92,
    'correlation': 0.78,
    'esg_score': 78,
    'portfolio_value': 2500000,
    'daily_pnl': 45000,
    'positions': [
      {'symbol': 'WTI', 'value': 1250000, 'pnl': 25000, 'risk': 'medium'},
      {'symbol': 'BRENT', 'value': 800000, 'pnl': 15000, 'risk': 'low'},
      {'symbol': 'NATURAL_GAS', 'value': 450000, 'pnl': 5000, 'risk': 'high'},
    ]
  };

  // Animation controllers
  late AnimationController _pulseAnimationController;
  late AnimationController _rotationAnimationController;
  late AnimationController _scaleAnimationController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _rotationAnimation;
  late Animation<double> _scaleAnimation;

  // AR Nodes
  List<ARNode> arNodes = [];
  ARAnchor? dashboardAnchor;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeAR();
    _loadRiskData();
  }

  void _initializeAnimations() {
    _pulseAnimationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _rotationAnimationController = AnimationController(
      duration: const Duration(seconds: 10),
      vsync: this,
    );
    _scaleAnimationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseAnimationController,
      curve: Curves.easeInOut,
    ));

    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 2 * pi,
    ).animate(CurvedAnimation(
      parent: _rotationAnimationController,
      curve: Curves.linear,
    ));

    _scaleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _scaleAnimationController,
      curve: Curves.elasticOut,
    ));

    _pulseAnimationController.repeat(reverse: true);
    _rotationAnimationController.repeat();
  }

  Future<void> _initializeAR() async {
    try {
      arSessionManager = ARSessionManager();
      arObjectManager = ARObjectManager(arSessionManager.session);
      arAnchorManager = ARAnchorManager(arSessionManager.session);
      arLocationManager = ARLocationManager(arSessionManager.session);

      await arSessionManager.initialize(
        config: ARPlaneDetectionConfig(
          horizontal: true,
          vertical: false,
        ),
      );

      setState(() {
        isARInitialized = true;
      });
    } catch (e) {
      _showErrorDialog('Failed to initialize AR: $e');
    }
  }

  void _loadRiskData() {
    if (widget.riskData != null) {
      setState(() {
        riskMetrics = widget.riskData!;
      });
    }
  }

  void _onARViewCreated(ARSessionManager arSessionManager) {
    this.arSessionManager = arSessionManager;
    this.arObjectManager = ARObjectManager(arSessionManager.session);
    this.arAnchorManager = ARAnchorManager(arSessionManager.session);
    this.arLocationManager = ARLocationManager(arSessionManager.session);

    arSessionManager.onInitialize(
      showFeaturePoints: false,
      showPlanes: true,
      customPlaneTexturePath: null,
      showWorldOrigin: false,
      handlePans: true,
      handleRotation: true,
    );

    arSessionManager.onPlaneOrPointTap = _onPlaneTapped;
  }

  Future<void> _onPlaneTapped(List<ARHitTestResult> hitTestResults) async {
    if (hitTestResults.isNotEmpty && !isDashboardVisible) {
      final hit = hitTestResults.first;
      final anchor = ARPlaneAnchor(transformation: hit.worldTransform);
      
      await _createARDashboard(anchor);
      setState(() {
        isDashboardVisible = true;
        dashboardAnchor = anchor;
      });
      
      _scaleAnimationController.forward();
    }
  }

  Future<void> _createARDashboard(ARAnchor anchor) async {
    // Create main dashboard container
    final dashboardContainer = ARNode(
      type: NodeType.webGLB,
      uri: 'assets/models/dashboard_container.glb',
      scale: Vector3(0.2, 0.2, 0.2),
      position: Vector3(0, 0, 0),
      rotation: Vector4(0, 0, 0, 0),
    );

    await arObjectManager.addNode(dashboardContainer, planeAnchor: anchor);
    arNodes.add(dashboardContainer);

    // Create risk metrics visualizations
    await _createRiskVisualizations(anchor);
    
    // Create portfolio 3D chart
    await _createPortfolioChart(anchor);
    
    // Create ESG score indicator
    await _createESGIndicator(anchor);
    
    // Create VaR visualization
    await _createVaRVisualization(anchor);
  }

  Future<void> _createRiskVisualizations(ARAnchor anchor) async {
    // VaR 95% indicator
    final var95Node = ARNode(
      type: NodeType.text,
      text: 'VaR 95%: \$${riskMetrics['var_95']}',
      scale: Vector3(0.03, 0.03, 0.03),
      position: Vector3(-0.3, 0.2, 0),
    );

    await arObjectManager.addNode(var95Node, planeAnchor: anchor);
    arNodes.add(var95Node);

    // VaR 99% indicator
    final var99Node = ARNode(
      type: NodeType.text,
      text: 'VaR 99%: \$${riskMetrics['var_99']}',
      scale: Vector3(0.03, 0.03, 0.03),
      position: Vector3(-0.3, 0.1, 0),
    );

    await arObjectManager.addNode(var99Node, planeAnchor: anchor);
    arNodes.add(var99Node);

    // Sharpe ratio indicator
    final sharpeNode = ARNode(
      type: NodeType.text,
      text: 'Sharpe: ${riskMetrics['sharpe_ratio']}',
      scale: Vector3(0.03, 0.03, 0.03),
      position: Vector3(-0.3, 0.0, 0),
    );

    await arObjectManager.addNode(sharpeNode, planeAnchor: anchor);
    arNodes.add(sharpeNode);

    // Max drawdown indicator
    final drawdownNode = ARNode(
      type: NodeType.text,
      text: 'Max DD: ${riskMetrics['max_drawdown']}%',
      scale: Vector3(0.03, 0.03, 0.03),
      position: Vector3(-0.3, -0.1, 0),
    );

    await arObjectManager.addNode(drawdownNode, planeAnchor: anchor);
    arNodes.add(drawdownNode);
  }

  Future<void> _createPortfolioChart(ARAnchor anchor) async {
    // Create 3D bar chart for portfolio positions
    final positions = riskMetrics['positions'] as List<dynamic>;
    
    for (int i = 0; i < positions.length; i++) {
      final position = positions[i];
      final height = (position['value'] / 1000000) * 0.5; // Scale to meters
      
      final barNode = ARNode(
        type: NodeType.cube,
        scale: Vector3(0.05, height, 0.05),
        position: Vector3(0.1 + (i * 0.1), height / 2, 0),
        rotation: Vector4(0, 0, 0, 0),
      );

      await arObjectManager.addNode(barNode, planeAnchor: anchor);
      arNodes.add(barNode);

      // Add position label
      final labelNode = ARNode(
        type: NodeType.text,
        text: '${position['symbol']}\n\$${position['value']}',
        scale: Vector3(0.02, 0.02, 0.02),
        position: Vector3(0.1 + (i * 0.1), height + 0.05, 0),
      );

      await arObjectManager.addNode(labelNode, planeAnchor: anchor);
      arNodes.add(labelNode);
    }
  }

  Future<void> _createESGIndicator(ARAnchor anchor) async {
    final esgScore = riskMetrics['esg_score'];
    final esgColor = esgScore >= 80 ? 'green' : esgScore >= 60 ? 'yellow' : 'red';
    
    final esgNode = ARNode(
      type: NodeType.sphere,
      scale: Vector3(0.1, 0.1, 0.1),
      position: Vector3(0.3, 0.2, 0),
    );

    await arObjectManager.addNode(esgNode, planeAnchor: anchor);
    arNodes.add(esgNode);

    // ESG score text
    final esgTextNode = ARNode(
      type: NodeType.text,
      text: 'ESG: $esgScore',
      scale: Vector3(0.03, 0.03, 0.03),
      position: Vector3(0.3, 0.1, 0),
    );

    await arObjectManager.addNode(esgTextNode, planeAnchor: anchor);
    arNodes.add(esgTextNode);
  }

  Future<void> _createVaRVisualization(ARAnchor anchor) async {
    // Create risk cone visualization
    final riskCone = ARNode(
      type: NodeType.cone,
      scale: Vector3(0.15, 0.3, 0.15),
      position: Vector3(0.0, 0.15, -0.2),
      rotation: Vector4(pi, 0, 0, 0),
    );

    await arObjectManager.addNode(riskCone, planeAnchor: anchor);
    arNodes.add(riskCone);

    // Risk level indicator
    final riskLevel = _calculateRiskLevel();
    final riskTextNode = ARNode(
      type: NodeType.text,
      text: 'Risk Level: $riskLevel',
      scale: Vector3(0.03, 0.03, 0.03),
      position: Vector3(0.0, 0.0, -0.2),
    );

    await arObjectManager.addNode(riskTextNode, planeAnchor: anchor);
    arNodes.add(riskTextNode);
  }

  String _calculateRiskLevel() {
    final var95 = riskMetrics['var_95'];
    final portfolioValue = riskMetrics['portfolio_value'];
    final riskRatio = var95 / portfolioValue;
    
    if (riskRatio < 0.02) return 'Low';
    if (riskRatio < 0.05) return 'Medium';
    return 'High';
  }

  void _switchView(String view) {
    setState(() {
      selectedView = view;
    });
    
    // Update AR visualizations based on selected view
    _updateARVisualizations(view);
  }

  Future<void> _updateARVisualizations(String view) async {
    if (dashboardAnchor == null) return;

    // Remove existing nodes
    for (final node in arNodes) {
      await arObjectManager.removeNode(node);
    }
    arNodes.clear();

    // Recreate visualizations for selected view
    switch (view) {
      case 'overview':
        await _createRiskVisualizations(dashboardAnchor!);
        await _createPortfolioChart(dashboardAnchor!);
        break;
      case 'risk':
        await _createVaRVisualization(dashboardAnchor!);
        await _createRiskVisualizations(dashboardAnchor!);
        break;
      case 'esg':
        await _createESGIndicator(dashboardAnchor!);
        break;
      case 'portfolio':
        await _createPortfolioChart(dashboardAnchor!);
        break;
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _resetDashboard() {
    setState(() {
      isDashboardVisible = false;
      selectedView = 'overview';
    });
    
    // Clear AR nodes
    for (final node in arNodes) {
      arObjectManager.removeNode(node);
    }
    arNodes.clear();
    dashboardAnchor = null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AR Risk Dashboard'),
        backgroundColor: Colors.blue[900],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: _resetDashboard,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: Stack(
        children: [
          // AR View
          if (isARInitialized)
            ARView(
              onARViewCreated: _onARViewCreated,
              planeDetectionConfig: const PlaneDetectionConfig(
                horizontal: true,
                vertical: false,
              ),
            )
          else
            const Center(
              child: CircularProgressIndicator(),
            ),

          // Overlay UI
          if (isDashboardVisible)
            Positioned(
              top: 20,
              left: 20,
              right: 20,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.8),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'AR Risk Dashboard',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    
                    // View selection buttons
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildViewButton('overview', 'Overview'),
                        _buildViewButton('risk', 'Risk'),
                        _buildViewButton('esg', 'ESG'),
                        _buildViewButton('portfolio', 'Portfolio'),
                      ],
                    ),
                    
                    const SizedBox(height: 12),
                    
                    // Key metrics
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _buildMetricCard('VaR 95%', '\$${riskMetrics['var_95']}', Colors.red),
                        _buildMetricCard('Portfolio', '\$${riskMetrics['portfolio_value']}', Colors.green),
                        _buildMetricCard('ESG', '${riskMetrics['esg_score']}', Colors.blue),
                      ],
                    ),
                  ],
                ),
              ),
            ),

          // Instructions overlay
          if (!isDashboardVisible)
            Positioned(
              bottom: 100,
              left: 20,
              right: 20,
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.touch_app,
                      color: Colors.white,
                      size: 48,
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Tap on a surface to place the AR Risk Dashboard',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Make sure the surface is well-lit and flat',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),

          // Risk alerts
          if (riskMetrics['var_95'] > 200000)
            Positioned(
              top: 100,
              right: 20,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.warning, color: Colors.white),
                    SizedBox(width: 8),
                    Text(
                      'High Risk Alert',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildViewButton(String view, String label) {
    final isSelected = selectedView == view;
    return GestureDetector(
      onTap: () => _switchView(view),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue : Colors.grey[700],
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: Colors.white,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Widget _buildMetricCard(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color),
      ),
      child: Column(
        children: [
          Text(
            title,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _pulseAnimationController.dispose();
    _rotationAnimationController.dispose();
    _scaleAnimationController.dispose();
    super.dispose();
  }
}
