import { FC } from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  ElectricBolt as ElectricBoltIcon,
  AccountBalance as AccountBalanceIcon,
  Percent as PercentIcon,
} from '@mui/icons-material';

interface EnergyScheduleSummaryCardsProps {
  totalEnergySavings: number;
  averageCTULosses: number;
  totalCost: number;
  daysCompleted: number;
}

const EnergyScheduleSummaryCards: FC<EnergyScheduleSummaryCardsProps> = ({
  totalEnergySavings,
  averageCTULosses,
  totalCost,
  daysCompleted,
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const cards = [
    {
      title: 'Total Energy Savings',
      value: `${totalEnergySavings.toFixed(2)} MWh`,
      icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
      color: '#10b981',
      subtitle: `${daysCompleted} days completed`,
    },
    {
      title: 'Average CTU Losses',
      value: `${averageCTULosses.toFixed(2)}%`,
      icon: <PercentIcon sx={{ fontSize: 40 }} />,
      color: '#f59e0b',
      subtitle: 'Transmission losses',
    },
    {
      title: 'Total Cost',
      value: formatCurrency(totalCost),
      icon: <AccountBalanceIcon sx={{ fontSize: 40 }} />,
      color: '#3b82f6',
      subtitle: 'NLDC + CTU Charges',
    },
    {
      title: 'Energy Efficiency',
      value: averageCTULosses > 0 ? `${(100 - averageCTULosses).toFixed(2)}%` : '-',
      icon: <ElectricBoltIcon sx={{ fontSize: 40 }} />,
      color: '#8b5cf6',
      subtitle: 'After transmission',
    },
  ];

  return (
    <Grid container spacing={3}>
      {cards.map((card, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              height: '100%',
              background: `linear-gradient(135deg, ${card.color}15 0%, ${card.color}05 100%)`,
              border: `1px solid ${card.color}30`,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
              <Typography variant="body2" color="text.secondary" fontWeight="medium">
                {card.title}
              </Typography>
              <Box sx={{ color: card.color, opacity: 0.8 }}>{card.icon}</Box>
            </Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 1 }}>
              {card.value}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {card.subtitle}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};

export default EnergyScheduleSummaryCards;
