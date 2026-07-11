import { FC, ReactNode } from 'react';
import {
  AppBar,
  Box,
  Button,
  Container,
  Divider,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

interface PublicLayoutProps {
  children: ReactNode;
}

const navItems = [
  { label: 'Platform', to: '/platform' },
  { label: 'Pricing', to: '/pricing' },
  { label: 'Partners', to: '/partners' },
  { label: 'Careers', to: '/careers' },
  { label: 'Contact', to: '/contact' },
];

const PublicLayout: FC<PublicLayoutProps> = ({ children }) => {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc', color: '#0f172a' }}>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          bgcolor: 'rgba(255,255,255,0.92)',
          color: '#0f172a',
          borderBottom: '1px solid #e2e8f0',
          backdropFilter: 'blur(14px)',
        }}
      >
        <Container maxWidth="xl">
          <Toolbar disableGutters sx={{ gap: 3 }}>
            <Typography
              component={RouterLink}
              to="/"
              variant="h6"
              sx={{
                color: 'inherit',
                flexGrow: 1,
                fontWeight: 800,
                letterSpacing: '-0.03em',
                textDecoration: 'none',
              }}
            >
              Innowatt Energy AI
            </Typography>

            <Stack
              direction="row"
              spacing={1}
              sx={{ display: { xs: 'none', md: 'flex' } }}
            >
              {navItems.map((item) => (
                <Button
                  key={item.to}
                  component={RouterLink}
                  to={item.to}
                  color="inherit"
                  sx={{ textTransform: 'none', fontWeight: 700 }}
                >
                  {item.label}
                </Button>
              ))}
            </Stack>

            <Button
              component={RouterLink}
              to="/login"
              variant="outlined"
              sx={{ textTransform: 'none', fontWeight: 800 }}
            >
              Login
            </Button>
            <Button
              component={RouterLink}
              to="/contact"
              variant="contained"
              sx={{ textTransform: 'none', fontWeight: 800 }}
            >
              Request Demo
            </Button>
          </Toolbar>
        </Container>
      </AppBar>

      {children}

      <Box component="footer" sx={{ bgcolor: '#0f172a', color: 'white', py: 6, mt: 8 }}>
        <Container maxWidth="xl">
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={4} justifyContent="space-between">
            <Box>
              <Typography variant="h6" fontWeight={900}>
                Innowatt Energy AI Solutions
              </Typography>
              <Typography color="#cbd5e1" sx={{ mt: 1, maxWidth: 520 }}>
                Transformative power trading intelligence for enterprises managing Solar, IEX,
                TNEB, schedules, and portfolio-level procurement decisions.
              </Typography>
            </Box>
            <Stack direction="row" spacing={3} flexWrap="wrap">
              {navItems.map((item) => (
                <Button
                  key={item.to}
                  component={RouterLink}
                  to={item.to}
                  sx={{ color: '#cbd5e1', textTransform: 'none' }}
                >
                  {item.label}
                </Button>
              ))}
            </Stack>
          </Stack>
          <Divider sx={{ my: 4, borderColor: '#334155' }} />
          <Typography variant="body2" color="#94a3b8">
            © {new Date().getFullYear()} Innowatt Energy AI Solutions. Enterprise energy
            intelligence platform.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default PublicLayout;
