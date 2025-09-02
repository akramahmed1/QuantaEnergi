import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, Typography, Grid, Box, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, Assessment, AccountBalance } from '@mui/icons-material';
import apiService from '../services/api';

const MarketOverview = () => {
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: apiService.getUserAnalytics,
    staleTime: 30000, // 30 seconds
    retry: 3
  });

  const { data: marketPrices, isLoading: pricesLoading } = useQuery({
    queryKey: ['marketPrices'],
    queryFn: apiService.getMarketPrices,
    staleTime: 15000, // 15 seconds
    retry: 3
  });

  if (isLoading || pricesLoading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4].map((item) => (
          <Grid item xs={12} sm={6} md={3} key={item}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="center" minHeight={120}>
                  <Typography variant="body2" color="text.secondary">
                    Loading...
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Typography color="error" variant="body2">
            Failed to load market overview: {error.message}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const marketPerformance = analytics?.market_perf || '+12.5%';
  const riskScore = analytics?.risk_score || 35;
  const portfolioValue = analytics?.portfolio_value || 125000;
  const dailyReturn = analytics?.daily_return || 2.5;

  const getPerformanceColor = (value) => {
    if (typeof value === 'string') {
      return value.includes('+') ? 'success' : 'error';
    }
    return value >= 0 ? 'success' : 'error';
  };

  const getRiskColor = (score) => {
    if (score <= 30) return 'success';
    if (score <= 60) return 'warning';
    return 'error';
  };

  const getRiskLabel = (score) => {
    if (score <= 30) return 'Low';
    if (score <= 60) return 'Medium';
    return 'High';
  };

  const metrics = [
    {
      title: 'Market Performance',
      value: marketPerformance,
      icon: <TrendingUp />,
      color: getPerformanceColor(marketPerformance),
      subtitle: '24h Change'
    },
    {
      title: 'Portfolio Value',
      value: `$${(portfolioValue / 1000).toFixed(1)}K`,
      icon: <AccountBalance />,
      color: 'primary',
      subtitle: 'Total Assets'
    },
    {
      title: 'Daily Return',
      value: `${dailyReturn > 0 ? '+' : ''}${dailyReturn}%`,
      icon: <TrendingUp />,
      color: getPerformanceColor(dailyReturn),
      subtitle: 'Today\'s P&L'
    },
    {
      title: 'Risk Score',
      value: getRiskLabel(riskScore),
      icon: <Assessment />,
      color: getRiskColor(riskScore),
      subtitle: `Score: ${riskScore}/100`
    }
  ];

  return (
    <Box mb={4}>
      <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 600, color: 'text.primary' }}>
        Market Overview
      </Typography>
      
      <Grid container spacing={3}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              elevation={2}
              sx={{ 
                height: '100%',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  elevation: 4,
                  transform: 'translateY(-2px)'
                }
              }}
            >
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Box
                    sx={{
                      backgroundColor: `${metric.color}.light`,
                      borderRadius: '50%',
                      p: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {React.cloneElement(metric.icon, { 
                      sx: { color: `${metric.color}.main`, fontSize: 24 } 
                    })}
                  </Box>
                  <Chip 
                    label={metric.subtitle} 
                    size="small" 
                    color={metric.color}
                    variant="outlined"
                  />
                </Box>
                
                <Typography variant="h4" component="div" gutterBottom sx={{ fontWeight: 700 }}>
                  {metric.value}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  {metric.title}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Market Prices Summary */}
      {marketPrices && (
        <Box mt={4}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Live Market Prices
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(marketPrices).map(([commodity, data]) => (
              <Grid item xs={12} sm={6} md={4} key={commodity}>
                <Card variant="outlined">
                  <CardContent sx={{ py: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle1" sx={{ textTransform: 'capitalize', fontWeight: 600 }}>
                        {commodity.replace('_', ' ')}
                      </Typography>
                      <Chip 
                        label={data.change} 
                        size="small" 
                        color={data.change.includes('+') ? 'success' : 'error'}
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, mt: 1 }}>
                      ${data.price}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Source: {data.source}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default MarketOverview;
