import { FC } from 'react';
import { CssBaseline } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppShell from './pages/AppShell';
import SaasHome from './pages/public/SaasHome';
import Pricing from './pages/public/Pricing';
import Login from './pages/public/Login';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2563eb',
    },
    secondary: {
      main: '#10b981',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: {
    borderRadius: 12,
  },
});

const App: FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SaasHome />} />
          <Route path="/platform" element={<SaasHome page="platform" />} />
          <Route path="/partners" element={<SaasHome page="partners" />} />
          <Route path="/careers" element={<SaasHome page="careers" />} />
          <Route path="/contact" element={<SaasHome page="contact" />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/app/*" element={<AppShell />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
