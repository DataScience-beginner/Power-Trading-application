import { FC } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import PublicLayout from '../../layouts/PublicLayout';

const plans = [
  {
    name: 'Starter Intelligence',
    audience: 'Single client / pilot portfolio',
    price: 'Contact Sales',
    features: [
      'Client workspace setup',
      'Portfolio dashboard',
      'DAM / RTM / GDAM upload support',
      'SCH and DOR visibility',
      'Basic reports',
    ],
  },
  {
    name: 'Professional Operations',
    audience: 'Multiple portfolios and recurring operations',
    price: 'Custom',
    highlighted: true,
    features: [
      'Multi-portfolio dashboards',
      'Energy schedule calculation',
      'Solar / IEX / TNEB cost analysis',
      'Workbook ingestion workflows',
      'Admin client switching',
    ],
  },
  {
    name: 'Enterprise AI',
    audience: 'AI-led procurement and automation',
    price: 'Custom',
    features: [
      'AI demand forecasting roadmap',
      'IEX price prediction roadmap',
      'Agentic email/file ingestion',
      'Custom integrations',
      'Executive reports and advisory support',
    ],
  },
];

const Pricing: FC = () => {
  return (
    <PublicLayout>
      <Container maxWidth="xl" sx={{ py: 10 }}>
        <Stack spacing={5}>
          <Box textAlign="center">
            <Chip label="Enterprise pricing" color="primary" />
            <Typography variant="h2" fontWeight={900} letterSpacing="-0.05em" sx={{ mt: 2 }}>
              Pricing that follows your operating complexity
            </Typography>
            <Typography color="text.secondary" variant="h6" sx={{ mt: 2, maxWidth: 820, mx: 'auto' }}>
              Innowatt is enterprise-focused. Early onboarding is configured with our team so
              client, portfolio, reporting, and procurement rules are modeled correctly.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {plans.map((plan) => (
              <Grid item xs={12} md={4} key={plan.name}>
                <Card
                  sx={{
                    height: '100%',
                    borderRadius: 5,
                    border: plan.highlighted ? '2px solid #2563eb' : '1px solid #e2e8f0',
                    boxShadow: plan.highlighted ? '0 24px 80px rgba(37,99,235,0.20)' : undefined,
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Stack spacing={3}>
                      {plan.highlighted && <Chip label="Recommended" color="primary" sx={{ alignSelf: 'flex-start' }} />}
                      <Box>
                        <Typography variant="h5" fontWeight={900}>
                          {plan.name}
                        </Typography>
                        <Typography color="text.secondary" sx={{ mt: 1 }}>
                          {plan.audience}
                        </Typography>
                      </Box>
                      <Typography variant="h4" fontWeight={900}>
                        {plan.price}
                      </Typography>
                      <Stack spacing={1.5}>
                        {plan.features.map((feature) => (
                          <Typography key={feature}>✓ {feature}</Typography>
                        ))}
                      </Stack>
                      <Button component={RouterLink} to="/contact" variant={plan.highlighted ? 'contained' : 'outlined'}>
                        Request Demo
                      </Button>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Stack>
      </Container>
    </PublicLayout>
  );
};

export default Pricing;
