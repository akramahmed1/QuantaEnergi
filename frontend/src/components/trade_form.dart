// Trade Form Component with Voice UI
// Provides speech-to-text functionality for trade capture with ME Arabic support

import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart';
import 'dart:async';

class TradeForm extends StatefulWidget {
  final Function(Map<String, dynamic>)? onTradeSubmitted;
  final String? initialCommodity;
  final String? language;

  const TradeForm({
    Key? key,
    this.onTradeSubmitted,
    this.initialCommodity,
    this.language = 'en',
  }) : super(key: key);

  @override
  _TradeFormState createState() => _TradeFormState();
}

class _TradeFormState extends State<TradeForm>
    with TickerProviderStateMixin {
  // Form controllers
  final _formKey = GlobalKey<FormState>();
  final _commodityController = TextEditingController();
  final _quantityController = TextEditingController();
  final _priceController = TextEditingController();
  final _counterpartyController = TextEditingController();
  final _deliveryDateController = TextEditingController();

  // Speech recognition
  final SpeechToText _speech = SpeechToText();
  bool _speechEnabled = false;
  bool _isListening = false;
  String _lastWords = '';
  String _currentLanguage = 'en';

  // Animation controllers
  late AnimationController _voiceAnimationController;
  late AnimationController _pulseAnimationController;
  late Animation<double> _voiceAnimation;
  late Animation<double> _pulseAnimation;

  // Form state
  String _selectedCommodity = 'crude_oil';
  String _selectedSide = 'buy';
  String _selectedCurrency = 'USD';
  DateTime? _selectedDeliveryDate;
  bool _isIslamicCompliant = false;

  // Voice command processing
  final Map<String, String> _voiceCommands = {
    'buy': 'buy',
    'sell': 'sell',
    'crude oil': 'crude_oil',
    'natural gas': 'natural_gas',
    'coal': 'coal',
    'renewables': 'renewables',
    'dollar': 'USD',
    'euro': 'EUR',
    'pound': 'GBP',
    'islamic': 'islamic_compliant',
    'sharia': 'islamic_compliant',
  };

  // Arabic voice commands
  final Map<String, String> _arabicVoiceCommands = {
    'شراء': 'buy',
    'بيع': 'sell',
    'النفط الخام': 'crude_oil',
    'الغاز الطبيعي': 'natural_gas',
    'الفحم': 'coal',
    'المتجددة': 'renewables',
    'دولار': 'USD',
    'يورو': 'EUR',
    'جنيه': 'GBP',
    'إسلامي': 'islamic_compliant',
    'شريعة': 'islamic_compliant',
  };

  @override
  void initState() {
    super.initState();
    _currentLanguage = widget.language ?? 'en';
    _selectedCommodity = widget.initialCommodity ?? 'crude_oil';
    _initializeAnimations();
    _initializeSpeech();
    _setupFormDefaults();
  }

  void _initializeAnimations() {
    _voiceAnimationController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    );
    _pulseAnimationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _voiceAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _voiceAnimationController,
      curve: Curves.easeInOut,
    ));

    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseAnimationController,
      curve: Curves.easeInOut,
    ));
  }

  Future<void> _initializeSpeech() async {
    try {
      // Request microphone permission
      var status = await Permission.microphone.request();
      if (status != PermissionStatus.granted) {
        _showErrorDialog('Microphone permission is required for voice input');
        return;
      }

      _speechEnabled = await _speech.initialize(
        onStatus: (status) {
          setState(() {
            _isListening = status == 'listening';
          });
        },
        onError: (error) {
          print('Speech error: $error');
          setState(() {
            _isListening = false;
          });
        },
      );
    } catch (e) {
      print('Speech initialization error: $e');
    }
  }

  void _setupFormDefaults() {
    _commodityController.text = _selectedCommodity;
    _quantityController.text = '1000';
    _priceController.text = '75.50';
    _counterpartyController.text = 'CP001';
    _deliveryDateController.text = DateFormat('yyyy-MM-dd')
        .format(DateTime.now().add(const Duration(days: 30)));
  }

  void _startListening() {
    if (!_speechEnabled) return;

    setState(() {
      _isListening = true;
    });

    _pulseAnimationController.repeat(reverse: true);

    _speech.listen(
      onResult: (result) {
        setState(() {
          _lastWords = result.recognizedWords;
        });
        _processVoiceInput(result.recognizedWords);
      },
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 3),
      partialResults: true,
      localeId: _currentLanguage == 'ar' ? 'ar_SA' : 'en_US',
      onSoundLevelChange: (level) {
        // Handle sound level changes for visual feedback
      },
    );
  }

  void _stopListening() {
    setState(() {
      _isListening = false;
    });
    _pulseAnimationController.stop();
    _speech.stop();
  }

  void _processVoiceInput(String input) {
    final lowerInput = input.toLowerCase();
    final commands = _currentLanguage == 'ar' 
        ? _arabicVoiceCommands 
        : _voiceCommands;

    // Process voice commands
    for (final entry in commands.entries) {
      if (lowerInput.contains(entry.key.toLowerCase())) {
        _executeVoiceCommand(entry.value, input);
        break;
      }
    }

    // Extract numbers for quantity and price
    _extractNumbersFromInput(input);
  }

  void _executeVoiceCommand(String command, String input) {
    switch (command) {
      case 'buy':
        setState(() {
          _selectedSide = 'buy';
        });
        _showVoiceFeedback('Buy order selected');
        break;
      case 'sell':
        setState(() {
          _selectedSide = 'sell';
        });
        _showVoiceFeedback('Sell order selected');
        break;
      case 'crude_oil':
        setState(() {
          _selectedCommodity = 'crude_oil';
          _commodityController.text = 'crude_oil';
        });
        _showVoiceFeedback('Crude oil selected');
        break;
      case 'natural_gas':
        setState(() {
          _selectedCommodity = 'natural_gas';
          _commodityController.text = 'natural_gas';
        });
        _showVoiceFeedback('Natural gas selected');
        break;
      case 'coal':
        setState(() {
          _selectedCommodity = 'coal';
          _commodityController.text = 'coal';
        });
        _showVoiceFeedback('Coal selected');
        break;
      case 'renewables':
        setState(() {
          _selectedCommodity = 'renewables';
          _commodityController.text = 'renewables';
        });
        _showVoiceFeedback('Renewables selected');
        break;
      case 'USD':
        setState(() {
          _selectedCurrency = 'USD';
        });
        _showVoiceFeedback('USD currency selected');
        break;
      case 'EUR':
        setState(() {
          _selectedCurrency = 'EUR';
        });
        _showVoiceFeedback('EUR currency selected');
        break;
      case 'GBP':
        setState(() {
          _selectedCurrency = 'GBP';
        });
        _showVoiceFeedback('GBP currency selected');
        break;
      case 'islamic_compliant':
        setState(() {
          _isIslamicCompliant = !_isIslamicCompliant;
        });
        _showVoiceFeedback(_isIslamicCompliant 
            ? 'Islamic compliance enabled' 
            : 'Islamic compliance disabled');
        break;
    }
  }

  void _extractNumbersFromInput(String input) {
    // Extract quantity (look for numbers followed by volume keywords)
    final quantityRegex = RegExp(r'(\d+)\s*(barrels?|tons?|units?|volume)');
    final quantityMatch = quantityRegex.firstMatch(input.toLowerCase());
    if (quantityMatch != null) {
      setState(() {
        _quantityController.text = quantityMatch.group(1)!;
      });
      _showVoiceFeedback('Quantity set to ${quantityMatch.group(1)}');
    }

    // Extract price (look for numbers followed by price keywords)
    final priceRegex = RegExp(r'(\d+\.?\d*)\s*(dollars?|price|per barrel)');
    final priceMatch = priceRegex.firstMatch(input.toLowerCase());
    if (priceMatch != null) {
      setState(() {
        _priceController.text = priceMatch.group(1)!;
      });
      _showVoiceFeedback('Price set to ${priceMatch.group(1)}');
    }
  }

  void _showVoiceFeedback(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
        backgroundColor: Colors.blue,
      ),
    );
  }

  Future<void> _selectDeliveryDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _selectedDeliveryDate ?? DateTime.now().add(const Duration(days: 30)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (date != null) {
      setState(() {
        _selectedDeliveryDate = date;
        _deliveryDateController.text = DateFormat('yyyy-MM-dd').format(date);
      });
    }
  }

  void _submitTrade() {
    if (_formKey.currentState!.validate()) {
      final trade = {
        'side': _selectedSide,
        'commodity': _selectedCommodity,
        'quantity': double.parse(_quantityController.text),
        'price': double.parse(_priceController.text),
        'currency': _selectedCurrency,
        'counterparty': _counterpartyController.text,
        'delivery_date': _deliveryDateController.text,
        'islamic_compliant': _isIslamicCompliant,
        'timestamp': DateTime.now().toIso8601String(),
        'method': 'voice_input',
        'language': _currentLanguage,
      };

      widget.onTradeSubmitted?.call(trade);
      _showTradeConfirmation(trade);
    }
  }

  void _showTradeConfirmation(Map<String, dynamic> trade) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(_currentLanguage == 'ar' ? 'تم تنفيذ الصفقة' : 'Trade Executed'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${_currentLanguage == 'ar' ? 'الجانب' : 'Side'}: ${trade['side']?.toUpperCase()}'),
            Text('${_currentLanguage == 'ar' ? 'السلعة' : 'Commodity'}: ${trade['commodity']}'),
            Text('${_currentLanguage == 'ar' ? 'الكمية' : 'Quantity'}: ${trade['quantity']}'),
            Text('${_currentLanguage == 'ar' ? 'السعر' : 'Price'}: ${trade['currency']} ${trade['price']}'),
            Text('${_currentLanguage == 'ar' ? 'الطرف المقابل' : 'Counterparty'}: ${trade['counterparty']}'),
            Text('${_currentLanguage == 'ar' ? 'تاريخ التسليم' : 'Delivery Date'}: ${trade['delivery_date']}'),
            if (trade['islamic_compliant'])
              Text(_currentLanguage == 'ar' ? 'متوافق مع الشريعة الإسلامية' : 'Islamic Compliant'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(_currentLanguage == 'ar' ? 'موافق' : 'OK'),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(_currentLanguage == 'ar' ? 'خطأ' : 'Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(_currentLanguage == 'ar' ? 'موافق' : 'OK'),
          ),
        ],
      ),
    );
  }

  void _toggleLanguage() {
    setState(() {
      _currentLanguage = _currentLanguage == 'en' ? 'ar' : 'en';
    });
  }

  @override
  Widget build(BuildContext context) {
    final isRTL = _currentLanguage == 'ar';
    
    return Directionality(
      textDirection: isRTL ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Text(_currentLanguage == 'ar' ? 'نموذج التداول' : 'Trade Form'),
          backgroundColor: Colors.blue[900],
          foregroundColor: Colors.white,
          actions: [
            IconButton(
              onPressed: _toggleLanguage,
              icon: Text(_currentLanguage == 'ar' ? 'EN' : 'عربي'),
            ),
          ],
        ),
        body: Stack(
          children: [
            // Main form
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Voice input section
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.blue),
                      ),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                _currentLanguage == 'ar' 
                                    ? 'الإدخال الصوتي' 
                                    : 'Voice Input',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              AnimatedBuilder(
                                animation: _pulseAnimation,
                                builder: (context, child) {
                                  return Transform.scale(
                                    scale: _isListening ? _pulseAnimation.value : 1.0,
                                    child: IconButton(
                                      onPressed: _isListening ? _stopListening : _startListening,
                                      icon: Icon(
                                        _isListening ? Icons.mic : Icons.mic_none,
                                        color: _isListening ? Colors.red : Colors.blue,
                                        size: 32,
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ],
                          ),
                          if (_lastWords.isNotEmpty)
                            Container(
                              margin: const EdgeInsets.only(top: 8),
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.grey[200],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                _lastWords,
                                style: const TextStyle(fontSize: 16),
                              ),
                            ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Trade side selection
                    Row(
                      children: [
                        Expanded(
                          child: RadioListTile<String>(
                            title: Text(_currentLanguage == 'ar' ? 'شراء' : 'Buy'),
                            value: 'buy',
                            groupValue: _selectedSide,
                            onChanged: (value) {
                              setState(() {
                                _selectedSide = value!;
                              });
                            },
                          ),
                        ),
                        Expanded(
                          child: RadioListTile<String>(
                            title: Text(_currentLanguage == 'ar' ? 'بيع' : 'Sell'),
                            value: 'sell',
                            groupValue: _selectedSide,
                            onChanged: (value) {
                              setState(() {
                                _selectedSide = value!;
                              });
                            },
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Commodity selection
                    DropdownButtonFormField<String>(
                      value: _selectedCommodity,
                      decoration: InputDecoration(
                        labelText: _currentLanguage == 'ar' ? 'السلعة' : 'Commodity',
                        border: const OutlineInputBorder(),
                      ),
                      items: [
                        DropdownMenuItem(
                          value: 'crude_oil',
                          child: Text(_currentLanguage == 'ar' ? 'النفط الخام' : 'Crude Oil'),
                        ),
                        DropdownMenuItem(
                          value: 'natural_gas',
                          child: Text(_currentLanguage == 'ar' ? 'الغاز الطبيعي' : 'Natural Gas'),
                        ),
                        DropdownMenuItem(
                          value: 'coal',
                          child: Text(_currentLanguage == 'ar' ? 'الفحم' : 'Coal'),
                        ),
                        DropdownMenuItem(
                          value: 'renewables',
                          child: Text(_currentLanguage == 'ar' ? 'المتجددة' : 'Renewables'),
                        ),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedCommodity = value!;
                          _commodityController.text = value;
                        });
                      },
                    ),

                    const SizedBox(height: 16),

                    // Quantity input
                    TextFormField(
                      controller: _quantityController,
                      decoration: InputDecoration(
                        labelText: _currentLanguage == 'ar' ? 'الكمية' : 'Quantity',
                        border: const OutlineInputBorder(),
                        suffixText: _currentLanguage == 'ar' ? 'برميل' : 'barrels',
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return _currentLanguage == 'ar' 
                              ? 'يرجى إدخال الكمية' 
                              : 'Please enter quantity';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 16),

                    // Price input
                    TextFormField(
                      controller: _priceController,
                      decoration: InputDecoration(
                        labelText: _currentLanguage == 'ar' ? 'السعر' : 'Price',
                        border: const OutlineInputBorder(),
                        prefixText: _selectedCurrency + ' ',
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return _currentLanguage == 'ar' 
                              ? 'يرجى إدخال السعر' 
                              : 'Please enter price';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 16),

                    // Currency selection
                    DropdownButtonFormField<String>(
                      value: _selectedCurrency,
                      decoration: InputDecoration(
                        labelText: _currentLanguage == 'ar' ? 'العملة' : 'Currency',
                        border: const OutlineInputBorder(),
                      ),
                      items: [
                        DropdownMenuItem(
                          value: 'USD',
                          child: Text(_currentLanguage == 'ar' ? 'دولار أمريكي' : 'USD'),
                        ),
                        DropdownMenuItem(
                          value: 'EUR',
                          child: Text(_currentLanguage == 'ar' ? 'يورو' : 'EUR'),
                        ),
                        DropdownMenuItem(
                          value: 'GBP',
                          child: Text(_currentLanguage == 'ar' ? 'جنيه إسترليني' : 'GBP'),
                        ),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedCurrency = value!;
                        });
                      },
                    ),

                    const SizedBox(height: 16),

                    // Counterparty input
                    TextFormField(
                      controller: _counterpartyController,
                      decoration: InputDecoration(
                        labelText: _currentLanguage == 'ar' ? 'الطرف المقابل' : 'Counterparty',
                        border: const OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return _currentLanguage == 'ar' 
                              ? 'يرجى إدخال الطرف المقابل' 
                              : 'Please enter counterparty';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 16),

                    // Delivery date
                    TextFormField(
                      controller: _deliveryDateController,
                      decoration: InputDecoration(
                        labelText: _currentLanguage == 'ar' ? 'تاريخ التسليم' : 'Delivery Date',
                        border: const OutlineInputBorder(),
                        suffixIcon: const Icon(Icons.calendar_today),
                      ),
                      readOnly: true,
                      onTap: _selectDeliveryDate,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return _currentLanguage == 'ar' 
                              ? 'يرجى اختيار تاريخ التسليم' 
                              : 'Please select delivery date';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 16),

                    // Islamic compliance checkbox
                    CheckboxListTile(
                      title: Text(_currentLanguage == 'ar' 
                          ? 'متوافق مع الشريعة الإسلامية' 
                          : 'Islamic Compliant'),
                      value: _isIslamicCompliant,
                      onChanged: (value) {
                        setState(() {
                          _isIslamicCompliant = value!;
                        });
                      },
                    ),

                    const SizedBox(height: 32),

                    // Submit button
                    ElevatedButton(
                      onPressed: _submitTrade,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[900],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: Text(
                        _currentLanguage == 'ar' ? 'تنفيذ الصفقة' : 'Execute Trade',
                        style: const TextStyle(fontSize: 18),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Voice listening overlay
            if (_isListening)
              Positioned.fill(
                child: Container(
                  color: Colors.blue.withOpacity(0.1),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        AnimatedBuilder(
                          animation: _pulseAnimation,
                          builder: (context, child) {
                            return Transform.scale(
                              scale: _pulseAnimation.value,
                              child: const Icon(
                                Icons.mic,
                                size: 80,
                                color: Colors.red,
                              ),
                            );
                          },
                        ),
                        const SizedBox(height: 16),
                        Text(
                          _currentLanguage == 'ar' 
                              ? 'استمع...' 
                              : 'Listening...',
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.red,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _voiceAnimationController.dispose();
    _pulseAnimationController.dispose();
    _speech.stop();
    super.dispose();
  }
}
