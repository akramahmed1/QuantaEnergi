import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, Typography, Box, Grid, LinearProgress, Chip } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Eco, People, Security, TrendingUp } from '@mui/icons-material';
import apiService from '../services/api';

const ESGScore = () => {
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: apiService.getUserAnalytics,
    staleTime: 60000, // 1 minute
    retry: 3
  });

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" minHeight={200}>
            <Typography variant="body2" color="text.secondary">
              Loading ESG metrics...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Typography color="error" variant="body2">
            Failed to load ESG data: {error.message}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Use real data from analytics or fallback to mock data
  const esgData = analytics?.esg_metrics || {
    overall_esg_score: 78.0,
    environmental_score: 82.0,
    social_score: 75.0,
    governance_score: 79.0,
    carbon_offset: 150.5
  };

  const barChartData = [
    { name: 'Environmental', score: esgData.environmental_score, color: '#4caf50', icon: <Eco /> },
    { name: 'Social', score: esgData.social_score, color: '#2196f3', icon: <People /> },
    { name: 'Governance', score: esgData.governance_score, color: '#ff9800', icon: <Security /> }
  ];

  const pieChartData = [
    { name: 'Environmental', value: esgData.environmental_score, color: '#4caf50' },
    { name: 'Social', value: esgData.social_score, color: '#2196f3' },
    { name: 'Governance', value: esgData.governance_score, color: '#ff9800' }
  ];

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  return (
    <Box mb={4}>
      <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 600, color: 'text.primary' }}>
        ESG Performance Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Overall ESG Score */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Overall ESG Score
                </Typography>
                <Chip 
                  label={getScoreLabel(esgData.overall_esg_score)} 
                  color={getScoreColor(esgData.overall_esg_score)}
                  variant="outlined"
                />
              </Box>
              
              <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
                <Typography variant="h2" component="div" sx={{ 
                  fontWeight: 700, 
                  color: `${getScoreColor(esgData.overall_esg_score)}.main` 
                }}>
                  {esgData.overall_esg_score}
                </Typography>
                <Typography variant="h4" sx={{ ml: 1, color: 'text.secondary' }}>/100</Typography>
              </Box>
              
              <LinearProgress 
                variant="determinate" 
                value={esgData.overall_esg_score} 
                color={getScoreColor(esgData.overall_esg_score)}
                sx={{ height: 8, borderRadius: 4 }}
              />
              
              <Box display="flex" alignItems="center" mt={2}>
                <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  +2.3% from last month
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* ESG Breakdown Chart */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                ESG Breakdown
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value) => [`${value}/100`, 'Score']}
                    labelStyle={{ fontWeight: 600 }}
                  />
                  <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                    {barChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Carbon Offset & Sustainability */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Carbon Offset
              </Typography>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {esgData.carbon_offset} tons
                </Typography>
                <Eco sx={{ color: 'success.main', fontSize: 40 }} />
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                CO₂ equivalent offset this year
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((esgData.carbon_offset / 200) * 100, 100)} 
                color="success"
                sx={{ height: 6, borderRadius: 3 }}
              />
              <Typography variant="caption" color="text.secondary">
                Target: 200 tons annually
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* ESG Distribution Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                ESG Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => [`${value}/100`, 'Score']}
                    labelStyle={{ fontWeight: 600 }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <Box display="flex" justifyContent="center" mt={2}>
                {pieChartData.map((item, index) => (
                  <Box key={index} display="flex" alignItems="center" mx={1}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        backgroundColor: item.color,
                        borderRadius: '50%',
                        mr: 0.5
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {item.name}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ESGScore;
