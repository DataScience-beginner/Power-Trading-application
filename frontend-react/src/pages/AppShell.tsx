import { useEffect, useState, FC } from 'react';
import { Box, Toolbar } from '@mui/material';
import Navbar from '../components/Navbar';
import Sidebar, { type AppPage } from '../components/Sidebar';
import Dashboard from './Dashboard';
import EnergySchedule from './EnergySchedule';
import Analytics from './Analytics';
import Reports from './Reports';
import AIPredict from './AIPredict';
import AdminDatabase from './AdminDatabase';
import AdminLogin from './AdminLogin';
import WorkbookInputsPage from './WorkbookInputsPage';
import FileUploadDialog from '../components/FileUploadDialog';
import CalculateEnergyScheduleDialog from '../components/CalculateEnergyScheduleDialog';
import { useAppDispatch } from '../hooks/useAppStore';
import { fetchTransactions, fetchAnalytics, setFilter } from '../store/dashboardSlice';
import NewDashboard from './NewDashboard';

const allowedPages: AppPage[] = [
  'dashboard',
  'energySchedule',
  'analytics',
  'reports',
  'aiPredict',
  'adminDatabase',
  'newDashboard',
  'workbooks',
];

const AppShell: FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [calculateDialogOpen, setCalculateDialogOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState<AppPage>('dashboard');
  const dispatch = useAppDispatch();

  useEffect(() => {
    const applyPageFromUrl = () => {
      const url = new URL(window.location.href);
      const page = url.searchParams.get('page');
      if (page && allowedPages.includes(page as AppPage)) {
        setCurrentPage(page as AppPage);
      }
    };

    applyPageFromUrl();
    window.addEventListener('popstate', applyPageFromUrl);
    return () => window.removeEventListener('popstate', applyPageFromUrl);
  }, []);

  const handlePortfolioSelect = (portfolio: string) => {
    dispatch(setFilter({ portfolio }));
  };

  const handleUploadSuccess = () => {
    const filter = {
      startDate: new Date(new Date().setMonth(new Date().getMonth() - 1))
        .toISOString()
        .split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
    };
    dispatch(fetchTransactions(filter));
    dispatch(fetchAnalytics(filter));
  };

  const handlePageChange = (page: AppPage) => {
    setCurrentPage(page);
    const url = new URL(window.location.href);
    url.searchParams.set('page', page);
    window.history.pushState({}, '', url.toString());
  };

  const isAdmin = Boolean(localStorage.getItem('admin_jwt') || sessionStorage.getItem('admin_jwt'));

  return (
    <Box sx={{ display: 'flex' }}>
      <Navbar
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        onWorkbookInputsClick={() => handlePageChange('workbooks')}
        onUploadClick={() => setUploadDialogOpen(true)}
        onCalculateClick={() => setCalculateDialogOpen(true)}
        onAdminClick={() => handlePageChange('adminDatabase')}
      />
      <Sidebar
        open={sidebarOpen}
        onPortfolioSelect={handlePortfolioSelect}
        currentPage={currentPage}
        onPageChange={handlePageChange}
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
        {currentPage === 'adminDatabase' && (isAdmin ? <AdminDatabase /> : <AdminLogin onLogin={() => handlePageChange('adminDatabase')} />)}
        {currentPage === 'newDashboard' && <NewDashboard />}
        {currentPage === 'workbooks' && <WorkbookInputsPage />}
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
    </Box>
  );
};

export default AppShell;
