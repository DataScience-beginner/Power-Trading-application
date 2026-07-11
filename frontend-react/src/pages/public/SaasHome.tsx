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
import {
  AutoGraph,
  Bolt,
  Business,
  CloudUpload,
  Psychology,
  Savings,
  Security,
  SolarPower,
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import PublicLayout from '../../layouts/PublicLayout';

type InfoPageKind = 'home' | 'platform' | 'partners' | 'careers' | 'contact';

interface SaasHomeProps {
  page?: InfoPageKind;
}

const capabilities = [
  {
    icon: <CloudUpload />,
    title: 'Trading data ingestion',
    text: 'Upload and validate DAM, RTM, GDAM, SCH, DOR, and workbook inputs in one controlled workflow.',
  },
  {
    icon: <SolarPower />,
    title: 'Solar-first visibility',
    text: 'Track solar availability, consumption validity, and portfolio-level allocation before expiry.',
  },
  {
    icon: <Bolt />,
    title: 'IEX purchase planning',
    text: 'Estimate expected shortfall and prepare next-day purchase strategy when exchange power is cheaper.',
  },
  {
    icon: <Savings />,
    title: 'TNEB fallback control',
    text: 'Make costly fallback consumption visible so clients can reduce avoidable grid exposure.',
  },
  {
    icon: <AutoGraph />,
    title: 'Schedule analytics',
    text: 'Compare scheduled versus delivered positions, deviations, costs, and portfolio performance.',
  },
  {
    icon: <Psychology />,
    title: 'AI procurement roadmap',
    text: 'Move toward AI-assisted demand forecasting, price prediction, and procurement recommendations.',
  },
];

const workflow = [
  'Upload client reports',
  'Validate schema and gaps',
  'Calculate schedules',
  'Analyze Solar / IEX / TNEB mix',
  'Recommend next action',
  'Publish dashboard and reports',
];

const Hero = () => (
  <Box
    sx={{
      background:
        'radial-gradient(circle at top left, rgba(16,185,129,0.18), transparent 34%), linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #0f766e 100%)',
      color: 'white',
      py: { xs: 8, md: 12 },
    }}
  >
    <Container maxWidth="xl">
      <Grid container spacing={6} alignItems="center">
        <Grid item xs={12} md={7}>
          <Stack spacing={3}>
            <Chip
              label="Enterprise power trading intelligence"
              sx={{ alignSelf: 'flex-start', bgcolor: 'rgba(255,255,255,0.16)', color: 'white' }}
            />
            <Typography variant="h2" fontWeight={900} letterSpacing="-0.06em">
              Buy power smarter with AI-guided Solar, IEX, and TNEB planning.
            </Typography>
            <Typography variant="h6" color="#dbeafe" maxWidth={760}>
              Innowatt Energy AI Solutions helps enterprise energy teams forecast demand,
              analyze schedules, and plan procurement decisions before costly fallback power
              becomes unavoidable.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Button component={RouterLink} to="/contact" variant="contained" size="large">
                Request Demo
              </Button>
              <Button
                component={RouterLink}
                to="/login"
                variant="outlined"
                size="large"
                sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.55)' }}
              >
                Login to Platform
              </Button>
            </Stack>
          </Stack>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card sx={{ bgcolor: 'rgba(255,255,255,0.95)', borderRadius: 4 }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="overline" color="primary" fontWeight={900}>
                Procurement strategy engine
              </Typography>
              <Stack spacing={2} sx={{ mt: 2 }}>
                {[
                  ['Solar', 'Use before monthly validity expires', '#10b981'],
                  ['IEX', 'Buy when next-day price is attractive', '#3b82f6'],
                  ['TNEB', 'Minimize costly fallback exposure', '#f97316'],
                ].map(([source, text, color]) => (
                  <Box key={source} sx={{ p: 2, borderRadius: 3, bgcolor: '#f8fafc' }}>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Box sx={{ width: 12, height: 44, borderRadius: 2, bgcolor: color }} />
                      <Box>
                        <Typography color="#0f172a" fontWeight={900}>
                          {source}
                        </Typography>
                        <Typography color="#475569">{text}</Typography>
                      </Box>
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  </Box>
);

const HomeContent = () => (
  <>
    <Hero />
    <Container maxWidth="xl" sx={{ py: 8 }}>
      <Stack spacing={6}>
        <Box textAlign="center">
          <Typography variant="h3" fontWeight={900}>
            One platform for energy procurement clarity
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 2, maxWidth: 820, mx: 'auto' }}>
            Built for teams managing multiple clients, portfolios, report formats, and
            procurement sources — with a roadmap toward agentic AI automation.
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {capabilities.map((item) => (
            <Grid item xs={12} md={4} key={item.title}>
              <Card sx={{ height: '100%', borderRadius: 4 }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>{item.icon}</Box>
                  <Typography variant="h6" fontWeight={900}>
                    {item.title}
                  </Typography>
                  <Typography color="text.secondary" sx={{ mt: 1 }}>
                    {item.text}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Card sx={{ borderRadius: 5, bgcolor: '#0f172a', color: 'white' }}>
          <CardContent sx={{ p: { xs: 3, md: 5 } }}>
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={5}>
                <Typography variant="h4" fontWeight={900}>
                  From upload to recommendation
                </Typography>
                <Typography color="#cbd5e1" sx={{ mt: 2 }}>
                  The operating model is simple: collect the right data, validate it, calculate
                  the energy position, then help the client make a better procurement decision.
                </Typography>
              </Grid>
              <Grid item xs={12} md={7}>
                <Grid container spacing={2}>
                  {workflow.map((step, index) => (
                    <Grid item xs={12} sm={6} key={step}>
                      <Box sx={{ p: 2, borderRadius: 3, bgcolor: 'rgba(255,255,255,0.08)' }}>
                        <Typography color="#93c5fd" fontWeight={900}>
                          0{index + 1}
                        </Typography>
                        <Typography fontWeight={800}>{step}</Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Stack>
    </Container>
  </>
);

const SectionPage = ({ page }: { page: Exclude<InfoPageKind, 'home'> }) => {
  const content = {
    platform: {
      title: 'Platform',
      subtitle: 'A controlled operating system for enterprise power trading analysis.',
      points: ['Client and portfolio workspaces', 'Trading report ingestion', 'Energy schedule calculation', 'AI-ready analytics layer'],
    },
    partners: {
      title: 'Partners',
      subtitle: 'Built to collaborate with consultants, brokers, renewable providers, and enterprise energy teams.',
      points: ['Energy consultants', 'Open access and trading partners', 'Solar and renewable operators', 'Data and integration partners'],
    },
    careers: {
      title: 'Careers',
      subtitle: 'We are building a specialist-led, agentic AI-first company — not a manual operations factory.',
      points: ['Energy domain specialists', 'AI workflow architects', 'Full-stack product engineers', 'Data quality and analytics specialists'],
    },
    contact: {
      title: 'Request a demo',
      subtitle: 'For early clients, onboarding is sales-led and configured by the Innowatt team.',
      points: ['Share your client/portfolio structure', 'Review available DAM/RTM/GDAM/SCH/DOR reports', 'Configure dashboards', 'Plan AI procurement roadmap'],
    },
  }[page];

  return (
    <Container maxWidth="lg" sx={{ py: 10 }}>
      <Stack spacing={4}>
        <Chip label="Innowatt Energy AI Solutions" sx={{ alignSelf: 'flex-start' }} />
        <Typography variant="h2" fontWeight={900} letterSpacing="-0.05em">
          {content.title}
        </Typography>
        <Typography variant="h6" color="text.secondary" maxWidth={820}>
          {content.subtitle}
        </Typography>
        <Grid container spacing={3}>
          {content.points.map((point) => (
            <Grid item xs={12} md={6} key={point}>
              <Card sx={{ borderRadius: 4, height: '100%' }}>
                <CardContent sx={{ p: 3 }}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Security color="primary" />
                    <Typography fontWeight={900}>{point}</Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        {page === 'contact' && (
          <Button component={RouterLink} to="/login" variant="contained" size="large" sx={{ alignSelf: 'flex-start' }}>
            Continue to login options
          </Button>
        )}
      </Stack>
    </Container>
  );
};

const SaasHome: FC<SaasHomeProps> = ({ page = 'home' }) => {
  return (
    <PublicLayout>
      {page === 'home' ? <HomeContent /> : <SectionPage page={page} />}
    </PublicLayout>
  );
};

export default SaasHome;
