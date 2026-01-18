import { useState, FC } from 'react';
import { Box, CssBaseline, Toolbar } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import EnergySchedule from './pages/EnergySchedule';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import AIPredict from './pages/AIPredict';
import FileUploadDialog from './components/FileUploadDialog';
import CalculateEnergyScheduleDialog from './components/CalculateEnergyScheduleDialog';
import { useAppDispatch } from './hooks/useAppStore';
import { fetchTransactions, fetchAnalytics, setFilter } from './store/dashboardSlice';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3b82f6',
    },
    secondary: {
      main: '#10b981',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const App: FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [calculateDialogOpen, setCalculateDialogOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'energySchedule' | 'analytics' | 'reports' | 'aiPredict'>('dashboard');
  const dispatch = useAppDispatch();

  const handleMenuClick = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handlePortfolioSelect = (portfolio: string) => {
    dispatch(setFilter({ portfolio }));
  };

  const handleUploadSuccess = () => {
    // Refresh data after successful upload
    const filter = {
      startDate: new Date(new Date().setMonth(new Date().getMonth() - 1))
        .toISOString()
        .split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
    };
    dispatch(fetchTransactions(filter));
    dispatch(fetchAnalytics(filter));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <Navbar
          onMenuClick={handleMenuClick}
          onUploadClick={() => setUploadDialogOpen(true)}
          onCalculateClick={() => setCalculateDialogOpen(true)}
        />
        <Sidebar 
          open={sidebarOpen} 
          onPortfolioSelect={handlePortfolioSelect}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
        />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - ${sidebarOpen ? 260 : 0}px)` },
            ml: sidebarOpen ? '260px' : 0,
            transition: 'margin-left 0.3s',
          }}
        >
          <Toolbar />
          {currentPage === 'dashboard' && <Dashboard />}
          {currentPage === 'energySchedule' && <EnergySchedule />}
          {currentPage === 'analytics' && <Analytics />}
          {currentPage === 'reports' && <Reports />}
          {currentPage === 'aiPredict' && <AIPredict />}
        </Box>
      </Box>
      <FileUploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onSuccess={handleUploadSuccess}
      />
      <CalculateEnergyScheduleDialog
        open={calculateDialogOpen}
        onClose={() => setCalculateDialogOpen(false)}
        onSuccess={handleUploadSuccess}
      />
    </ThemeProvider>
  );
};

export default App;
