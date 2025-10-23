import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Grid, 
  Chip, 
  Button,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import { 
  DataGrid, 
  GridToolbar,
  GridActionsCellItem 
} from '@mui/x-data-grid';
import { 
  TrendingUp, 
  TrendingDown, 
  Notifications, 
  Refresh,
  Visibility,
  Star,
  StarBorder
} from '@mui/icons-material';
import apiService from '../services/api';

const TradingSignals = () => {
  const [selectedSignals, setSelectedSignals] = useState([]);
  const [liveSignal, setLiveSignal] = useState(null);

  // Mock trading signals data - in real app, this would come from API
  const mockSignals = [
    {
      id: 1,
      signal: 'BUY',
      commodity: 'Crude Oil',
      confidence: 85,
      price: 85.50,
      target: 88.00,
      stopLoss: 83.00,
      timeframe: '4H',
      source: 'AI Model',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 min ago
      risk: 'Low',
      volume: 'High',
      trend: 'Bullish'
    },
    {
      id: 2,
      signal: 'SELL',
      commodity: 'Natural Gas',
      confidence: 72,
      price: 3.20,
      target: 3.00,
      stopLoss: 3.35,
      timeframe: '1D',
      source: 'Technical Analysis',
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
      risk: 'Medium',
      volume: 'Medium',
      trend: 'Bearish'
    },
    {
      id: 3,
      signal: 'HOLD',
      commodity: 'Electricity',
      confidence: 68,
      price: 45.80,
      target: 46.50,
      stopLoss: 44.50,
      timeframe: '1W',
      source: 'Fundamental Analysis',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
      risk: 'Low',
      volume: 'Low',
      trend: 'Sideways'
    },
    {
      id: 4,
      signal: 'BUY',
      commodity: 'Carbon Credits',
      confidence: 91,
      price: 28.50,
      target: 32.00,
      stopLoss: 27.00,
      timeframe: '1D',
      source: 'ESG Model',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 min ago
      risk: 'Low',
      volume: 'High',
      trend: 'Bullish'
    }
  ];

  const [signals, setSignals] = useState(mockSignals);

  // Simulate real-time signal updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly update confidence scores
      setSignals(prevSignals => 
        prevSignals.map(signal => ({
          ...signal,
          confidence: Math.max(50, Math.min(95, signal.confidence + (Math.random() - 0.5) * 5))
        }))
      );
    }, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  // WebSocket connection for live signals (mock implementation)
  useEffect(() => {
    const mockWebSocket = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance of new signal
        const newSignal = {
          id: Date.now(),
          signal: Math.random() > 0.5 ? 'BUY' : 'SELL',
          commodity: ['Crude Oil', 'Natural Gas', 'Electricity', 'Carbon Credits'][Math.floor(Math.random() * 4)],
          confidence: Math.floor(Math.random() * 30) + 70,
          price: (Math.random() * 100 + 20).toFixed(2),
          target: (Math.random() * 10 + 5).toFixed(2),
          stopLoss: (Math.random() * 5 + 2).toFixed(2),
          timeframe: ['1H', '4H', '1D', '1W'][Math.floor(Math.random() * 4)],
          source: ['AI Model', 'Technical Analysis', 'Fundamental Analysis', 'ESG Model'][Math.floor(Math.random() * 4)],
          timestamp: new Date().toISOString(),
          risk: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
          volume: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
          trend: ['Bullish', 'Bearish', 'Sideways'][Math.floor(Math.random() * 3)]
        };
        
        setLiveSignal(newSignal);
        setSignals(prev => [newSignal, ...prev.slice(0, -1)]); // Add new, remove oldest
        
        // Clear live signal after 5 seconds
        setTimeout(() => setLiveSignal(null), 5000);
      }
    }, 15000); // Check every 15 seconds

    return () => clearInterval(mockWebSocket);
  }, []);

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY': return 'success';
      case 'SELL': return 'error';
      case 'HOLD': return 'warning';
      default: return 'default';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Low': return 'success';
      case 'Medium': return 'warning';
      case 'High': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'Bullish': return <TrendingUp sx={{ color: 'success.main' }} />;
      case 'Bearish': return <TrendingDown sx={{ color: 'error.main' }} />;
      case 'Sideways': return <Box sx={{ width: 20, height: 20, border: '2px solid #ff9800', borderRadius: '50%' }} />;
      default: return null;
    }
  };

  const columns = [
    {
      field: 'signal',
      headerName: 'Signal',
      width: 100,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          color={getSignalColor(params.value)}
          size="small"
          sx={{ fontWeight: 600 }}
        />
      )
    },
    {
      field: 'commodity',
      headerName: 'Commodity',
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {params.value}
        </Typography>
      )
    },
    {
      field: 'confidence',
      headerName: 'Confidence',
      width: 120,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <Typography variant="body2" sx={{ mr: 1, fontWeight: 600 }}>
            {params.value}%
          </Typography>
          <Box
            sx={{
              width: 40,
              height: 6,
              backgroundColor: 'grey.200',
              borderRadius: 3,
              overflow: 'hidden'
            }}
          >
            <Box
              sx={{
                width: `${params.value}%`,
                height: '100%',
                backgroundColor: params.value >= 80 ? 'success.main' : 
                               params.value >= 60 ? 'warning.main' : 'error.main',
                transition: 'width 0.3s ease'
              }}
            />
          </Box>
        </Box>
      )
    },
    {
      field: 'price',
      headerName: 'Current Price',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          ${params.value}
        </Typography>
      )
    },
    {
      field: 'target',
      headerName: 'Target',
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2" color="success.main" sx={{ fontWeight: 600 }}>
          ${params.value}
        </Typography>
      )
    },
    {
      field: 'stopLoss',
      headerName: 'Stop Loss',
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2" color="error.main" sx={{ fontWeight: 600 }}>
          ${params.value}
        </Typography>
      )
    },
    {
      field: 'timeframe',
      headerName: 'Timeframe',
      width: 80,
      renderCell: (params) => (
        <Chip label={params.value} size="small" variant="outlined" />
      )
    },
    {
      field: 'risk',
      headerName: 'Risk',
      width: 80,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          color={getRiskColor(params.value)}
          size="small"
        />
      )
    },
    {
      field: 'trend',
      headerName: 'Trend',
      width: 100,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          {getTrendIcon(params.value)}
          <Typography variant="caption" sx={{ ml: 1 }}>
            {params.value}
          </Typography>
        </Box>
      )
    },
    {
      field: 'source',
      headerName: 'Source',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value}
        </Typography>
      )
    },
    {
      field: 'timestamp',
      headerName: 'Time',
      width: 150,
      renderCell: (params) => (
        <Typography variant="caption" color="text.secondary">
          {new Date(params.value).toLocaleTimeString()}
        </Typography>
      )
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      type: 'actions',
      getActions: (params) => [
        <GridActionsCellItem
          icon={<Visibility />}
          label="View Details"
          onClick={() => handleViewSignal(params.row)}
        />,
        <GridActionsCellItem
          icon={selectedSignals.includes(params.row.id) ? <Star /> : <StarBorder />}
          label="Toggle Favorite"
          onClick={() => handleToggleFavorite(params.row.id)}
        />
      ]
    }
  ];

  const handleViewSignal = (signal) => {
    console.log('Viewing signal:', signal);
    // In real app, this would open a detailed modal
  };

  const handleToggleFavorite = (signalId) => {
    setSelectedSignals(prev => 
      prev.includes(signalId) 
        ? prev.filter(id => id !== signalId)
        : [...prev, signalId]
    );
  };

  const handleRefresh = () => {
    // In real app, this would refetch data
    console.log('Refreshing signals...');
  };

  return (
    <Box mb={4}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 600, color: 'text.primary' }}>
          Trading Signals Dashboard
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            size="small"
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Notifications />}
            size="small"
          >
            Alerts
          </Button>
        </Box>
      </Box>

      {/* Live Signal Alert */}
      {liveSignal && (
        <Alert 
          severity="info" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={() => setLiveSignal(null)}>
              Dismiss
            </Button>
          }
        >
          <strong>New Signal Alert!</strong> {liveSignal.signal} {liveSignal.commodity} - 
          Confidence: {liveSignal.confidence}% - Price: ${liveSignal.price}
        </Alert>
      )}

      {/* Signals Summary Cards */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" color="success.main" sx={{ fontWeight: 700 }}>
                {signals.filter(s => s.signal === 'BUY').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Buy Signals
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" color="error.main" sx={{ fontWeight: 700 }}>
                {signals.filter(s => s.signal === 'SELL').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sell Signals
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" color="warning.main" sx={{ fontWeight: 700 }}>
                {signals.filter(s => s.signal === 'HOLD').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Hold Signals
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" color="primary.main" sx={{ fontWeight: 700 }}>
                {Math.round(signals.reduce((acc, s) => acc + s.confidence, 0) / signals.length)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Confidence
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Signals DataGrid */}
      <Card elevation={2}>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={signals}
              columns={columns}
              pageSize={10}
              rowsPerPageOptions={[5, 10, 25]}
              checkboxSelection
              disableSelectionOnClick
              components={{
                Toolbar: GridToolbar
              }}
              componentsProps={{
                toolbar: {
                  showQuickFilter: true,
                  quickFilterProps: { debounceMs: 500 }
                }
              }}
              sx={{
                '& .MuiDataGrid-cell': {
                  borderBottom: '1px solid #f0f0f0'
                },
                '& .MuiDataGrid-columnHeaders': {
                  backgroundColor: '#fafafa',
                  borderBottom: '2px solid #e0e0e0'
                }
              }}
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TradingSignals;
