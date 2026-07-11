import { FC } from 'react';
import {
  Alert,
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
import { AdminPanelSettings, Business, Lock } from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import PublicLayout from '../../layouts/PublicLayout';

const Login: FC = () => {
  return (
    <PublicLayout>
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <Stack spacing={4}>
          <Box textAlign="center">
            <Chip icon={<Lock />} label="Secure workspace login" color="primary" />
            <Typography variant="h2" fontWeight={900} letterSpacing="-0.05em" sx={{ mt: 2 }}>
              Continue to your Innowatt workspace
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mt: 2, maxWidth: 760, mx: 'auto' }}>
              Admins can manage all clients. Client users should see only their own company,
              portfolios, schedules, reports, and profile data.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%', borderRadius: 5 }}>
                <CardContent sx={{ p: 4 }}>
                  <Stack spacing={3}>
                    <AdminPanelSettings color="primary" sx={{ fontSize: 44 }} />
                    <Box>
                      <Typography variant="h5" fontWeight={900}>
                        Admin Portal
                      </Typography>
                      <Typography color="text.secondary" sx={{ mt: 1 }}>
                        For Innowatt operators who onboard clients, switch between clients,
                        inspect data, upload files, and manage platform operations.
                      </Typography>
                    </Box>
                    <Button component={RouterLink} to="/app?page=adminDatabase" variant="contained" size="large">
                      Continue as Admin
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%', borderRadius: 5 }}>
                <CardContent sx={{ p: 4 }}>
                  <Stack spacing={3}>
                    <Business color="secondary" sx={{ fontSize: 44 }} />
                    <Box>
                      <Typography variant="h5" fontWeight={900}>
                        Client Portal
                      </Typography>
                      <Typography color="text.secondary" sx={{ mt: 1 }}>
                        For enterprise clients who need portfolio-level dashboards, energy
                        schedules, analytics, reports, and AI procurement insights.
                      </Typography>
                    </Box>
                    <Button component={RouterLink} to="/app" variant="outlined" size="large">
                      Continue to Client Workspace
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Alert severity="info">
            Phase 1 uses admin-led onboarding. Full client-specific authentication and row-level
            data scoping should be implemented as the next backend security milestone.
          </Alert>
        </Stack>
      </Container>
    </PublicLayout>
  );
};

export default Login;
