// AR Trade Execution Component for Flutter
// Provides augmented reality interface for rig scanning and trade execution

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:camera/camera.dart';
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
import 'package:speech_to_text/speech_to_text.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:async';
import 'dart:math';

class ARTradeExecution extends StatefulWidget {
  final String? commodity;
  final Function(Map<String, dynamic>)? onTradeExecuted;
  final Function(String)? onRigScanned;

  const ARTradeExecution({
    Key? key,
    this.commodity,
    this.onTradeExecuted,
    this.onRigScanned,
  }) : super(key: key);

  @override
  _ARTradeExecutionState createState() => _ARTradeExecutionState();
}

class _ARTradeExecutionState extends State<ARTradeExecution>
    with TickerProviderStateMixin {
  // AR Controllers
  late ARSessionManager arSessionManager;
  late ARObjectManager arObjectManager;
  late ARAnchorManager arAnchorManager;
  late ARLocationManager arLocationManager;

  // State variables
  bool isARInitialized = false;
  bool isScanning = false;
  bool isRecording = false;
  String scannedRigId = '';
  String currentCommodity = 'crude_oil';
  double currentPrice = 75.50;
  int currentVolume = 1000;

  // Speech recognition
  final SpeechToText _speech = SpeechToText();
  bool _speechEnabled = false;
  String _lastWords = '';

  // Animation controllers
  late AnimationController _scanAnimationController;
  late AnimationController _pulseAnimationController;
  late Animation<double> _scanAnimation;
  late Animation<double> _pulseAnimation;

  // AR Nodes for 3D objects
  List<ARNode> arNodes = [];

  @override
  void initState() {
    super.initState();
    currentCommodity = widget.commodity ?? 'crude_oil';
    _initializeAnimations();
    _initializeAR();
    _initializeSpeech();
  }

  void _initializeAnimations() {
    _scanAnimationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _pulseAnimationController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    );

    _scanAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _scanAnimationController,
      curve: Curves.easeInOut,
    ));

    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseAnimationController,
      curve: Curves.easeInOut,
    ));

    _pulseAnimationController.repeat(reverse: true);
  }

  Future<void> _initializeAR() async {
    try {
      // Request camera permission
      var status = await Permission.camera.request();
      if (status != PermissionStatus.granted) {
        _showErrorDialog('Camera permission is required for AR functionality');
        return;
      }

      // Initialize AR session
      arSessionManager = ARSessionManager();
      arObjectManager = ARObjectManager(arSessionManager.session);
      arAnchorManager = ARAnchorManager(arSessionManager.session);
      arLocationManager = ARLocationManager(arSessionManager.session);

      // Configure AR session
      await arSessionManager.initialize(
        config: ARPlaneDetectionConfig(
          horizontal: true,
          vertical: false,
        ),
      );

      setState(() {
        isARInitialized = true;
      });

      // Start scanning animation
      _scanAnimationController.repeat();
    } catch (e) {
      _showErrorDialog('Failed to initialize AR: $e');
    }
  }

  Future<void> _initializeSpeech() async {
    try {
      _speechEnabled = await _speech.initialize(
        onStatus: (status) => setState(() {}),
        onError: (error) => setState(() {}),
      );
    } catch (e) {
      print('Speech initialization error: $e');
    }
  }

  void _startScanning() {
    setState(() {
      isScanning = true;
    });
    _scanAnimationController.repeat();
  }

  void _stopScanning() {
    setState(() {
      isScanning = false;
    });
    _scanAnimationController.stop();
  }

  void _startVoiceRecording() {
    if (!_speechEnabled) return;

    setState(() {
      isRecording = true;
    });

    _speech.listen(
      onResult: (result) {
        setState(() {
          _lastWords = result.recognizedWords;
        });
        _processVoiceCommand(result.recognizedWords);
      },
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 3),
      partialResults: true,
      localeId: 'en_US',
      onSoundLevelChange: (level) {
        // Handle sound level changes for visual feedback
      },
    );
  }

  void _stopVoiceRecording() {
    setState(() {
      isRecording = false;
    });
    _speech.stop();
  }

  void _processVoiceCommand(String command) {
    final lowerCommand = command.toLowerCase();
    
    if (lowerCommand.contains('buy')) {
      _executeTrade('buy');
    } else if (lowerCommand.contains('sell')) {
      _executeTrade('sell');
    } else if (lowerCommand.contains('volume')) {
      _extractVolumeFromCommand(command);
    } else if (lowerCommand.contains('price')) {
      _extractPriceFromCommand(command);
    }
  }

  void _extractVolumeFromCommand(String command) {
    final regex = RegExp(r'(\d+)');
    final match = regex.firstMatch(command);
    if (match != null) {
      setState(() {
        currentVolume = int.parse(match.group(1)!);
      });
    }
  }

  void _extractPriceFromCommand(String command) {
    final regex = RegExp(r'(\d+\.?\d*)');
    final match = regex.firstMatch(command);
    if (match != null) {
      setState(() {
        currentPrice = double.parse(match.group(1)!);
      });
    }
  }

  void _executeTrade(String side) {
    final trade = {
      'side': side,
      'commodity': currentCommodity,
      'volume': currentVolume,
      'price': currentPrice,
      'rig_id': scannedRigId,
      'timestamp': DateTime.now().toIso8601String(),
      'method': 'ar_voice',
    };

    widget.onTradeExecuted?.call(trade);
    _showTradeConfirmation(trade);
  }

  void _showTradeConfirmation(Map<String, dynamic> trade) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Trade Executed'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Side: ${trade['side']?.toUpperCase()}'),
            Text('Commodity: ${trade['commodity']}'),
            Text('Volume: ${trade['volume']}'),
            Text('Price: \$${trade['price']}'),
            Text('Rig ID: ${trade['rig_id']}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _onARViewCreated(ARSessionManager arSessionManager) {
    this.arSessionManager = arSessionManager;
    this.arObjectManager = ARObjectManager(arSessionManager.session);
    this.arAnchorManager = ARAnchorManager(arSessionManager.session);
    this.arLocationManager = ARLocationManager(arSessionManager.session);

    // Set up AR tap handling
    arSessionManager.onInitialize(
      showFeaturePoints: false,
      showPlanes: true,
      customPlaneTexturePath: null,
      showWorldOrigin: false,
      handlePans: true,
      handleRotation: true,
    );

    // Handle plane taps
    arSessionManager.onPlaneOrPointTap = _onPlaneTapped;
  }

  Future<void> _onPlaneTapped(List<ARHitTestResult> hitTestResults) async {
    if (hitTestResults.isNotEmpty) {
      final hit = hitTestResults.first;
      
      // Create AR anchor at tapped location
      final anchor = ARPlaneAnchor(transformation: hit.worldTransform);
      
      // Add 3D trading interface at tapped location
      await _addTradingInterface(anchor);
    }
  }

  Future<void> _addTradingInterface(ARAnchor anchor) async {
    // Create 3D trading interface
    final tradingInterface = ARNode(
      type: NodeType.webGLB,
      uri: 'assets/models/trading_interface.glb',
      scale: Vector3(0.1, 0.1, 0.1),
      position: Vector3(0, 0, 0),
      rotation: Vector4(0, 0, 0, 0),
    );

    await arObjectManager.addNode(tradingInterface, planeAnchor: anchor);
    arNodes.add(tradingInterface);

    // Add price display
    final priceDisplay = ARNode(
      type: NodeType.text,
      text: 'Price: \$${currentPrice.toStringAsFixed(2)}',
      scale: Vector3(0.05, 0.05, 0.05),
      position: Vector3(0, 0.1, 0),
    );

    await arObjectManager.addNode(priceDisplay, planeAnchor: anchor);
    arNodes.add(priceDisplay);
  }

  void _scanRig() {
    // Simulate rig scanning
    setState(() {
      scannedRigId = 'RIG_${Random().nextInt(1000)}';
    });
    
    widget.onRigScanned?.call(scannedRigId);
    _showRigScanResult(scannedRigId);
  }

  void _showRigScanResult(String rigId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Rig Scanned'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Rig ID: $rigId'),
            Text('Commodity: $currentCommodity'),
            Text('Status: Active'),
            Text('Capacity: 10,000 barrels'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AR Trade Execution'),
        backgroundColor: Colors.blue[900],
        foregroundColor: Colors.white,
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
          Positioned(
            top: 20,
            left: 20,
            right: 20,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.7),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Commodity: ${currentCommodity.toUpperCase()}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Price: \$${currentPrice.toStringAsFixed(2)}',
                    style: const TextStyle(
                      color: Colors.green,
                      fontSize: 16,
                    ),
                  ),
                  Text(
                    'Volume: $currentVolume',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                  if (scannedRigId.isNotEmpty)
                    Text(
                      'Rig: $scannedRigId',
                      style: const TextStyle(
                        color: Colors.blue,
                        fontSize: 14,
                      ),
                    ),
                ],
              ),
            ),
          ),

          // Voice recognition status
          if (isRecording)
            Positioned(
              bottom: 100,
              left: 20,
              right: 20,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.8),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    AnimatedBuilder(
                      animation: _pulseAnimation,
                      builder: (context, child) {
                        return Transform.scale(
                          scale: _pulseAnimation.value,
                          child: const Icon(
                            Icons.mic,
                            color: Colors.white,
                            size: 32,
                          ),
                        );
                      },
                    ),
                    const SizedBox(width: 16),
                    const Text(
                      'Listening...',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // Control buttons
          Positioned(
            bottom: 20,
            left: 20,
            right: 20,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // Scan Rig button
                FloatingActionButton(
                  onPressed: _scanRig,
                  backgroundColor: Colors.blue,
                  child: const Icon(Icons.qr_code_scanner),
                ),

                // Voice recording button
                FloatingActionButton(
                  onPressed: isRecording ? _stopVoiceRecording : _startVoiceRecording,
                  backgroundColor: isRecording ? Colors.red : Colors.green,
                  child: Icon(isRecording ? Icons.mic : Icons.mic_none),
                ),

                // Buy button
                FloatingActionButton(
                  onPressed: () => _executeTrade('buy'),
                  backgroundColor: Colors.green,
                  child: const Icon(Icons.trending_up),
                ),

                // Sell button
                FloatingActionButton(
                  onPressed: () => _executeTrade('sell'),
                  backgroundColor: Colors.red,
                  child: const Icon(Icons.trending_down),
                ),
              ],
            ),
          ),

          // Scanning animation
          if (isScanning)
            Positioned.fill(
              child: AnimatedBuilder(
                animation: _scanAnimation,
                builder: (context, child) {
                  return CustomPaint(
                    painter: ScanningPainter(_scanAnimation.value),
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _scanAnimationController.dispose();
    _pulseAnimationController.dispose();
    _speech.stop();
    super.dispose();
  }
}

class ScanningPainter extends CustomPainter {
  final double animationValue;

  ScanningPainter(this.animationValue);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    // Draw scanning line
    final startY = size.height * animationValue;
    final endY = startY + 50;

    canvas.drawLine(
      Offset(0, startY),
      Offset(size.width, endY),
      paint,
    );

    // Draw scanning area
    final rect = Rect.fromLTWH(
      0,
      startY - 25,
      size.width,
      100,
    );

    canvas.drawRect(
      rect,
      Paint()..color = Colors.blue.withOpacity(0.1),
    );
  }

  @override
  bool shouldRepaint(ScanningPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}
