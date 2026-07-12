import { useEffect, useState, FC } from 'react';
import { Box, Toolbar } from '@mui/material';
import Navbar from '../components/Navbar';
import Sidebar, { type AppPage } from '../components/Sidebar';
import Dashboard from './Dashboard';
import EnergySchedule from './EnergySchedule';
import Analytics from './Analytics';
import Reports from './Reports';
import AIPredict from './AIPredict';
import AIInsights from './AIInsights';
import AdminDatabase from './AdminDatabase';
import WorkbookInputsPage from './WorkbookInputsPage';
import MarketSnapshot from './MarketSnapshot';
import UploadCenter from './UploadCenter';
import FileUploadDialog from '../components/FileUploadDialog';
import CalculateEnergyScheduleDialog from '../components/CalculateEnergyScheduleDialog';
import { useAppDispatch } from '../hooks/useAppStore';
import { fetchTransactions, fetchAnalytics, setFilter } from '../store/dashboardSlice';
import NewDashboard from './NewDashboard';
import ChatAssistant from '../components/chat/ChatAssistant';
import { Navigate } from 'react-router-dom';

const allowedPages: AppPage[] = [
  'dashboard',
  'marketSnapshot',
  'uploadCenter',
  'energySchedule',
  'analytics',
  'reports',
  'aiPredict',
  'aiInsights',
  'adminDatabase',
  'newDashboard',
  'workbooks',
];

const AppShell: FC = () => {
  const accessToken = sessionStorage.getItem('innowatt_access_token');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [calculateDialogOpen, setCalculateDialogOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
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

  const storedUser = sessionStorage.getItem('innowatt_user');
  const isAdmin = storedUser ? JSON.parse(storedUser).role === 'platform_admin' : false;

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <Navbar
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        onWorkbookInputsClick={() => handlePageChange('workbooks')}
        onUploadClick={() => setUploadDialogOpen(true)}
        onCalculateClick={() => setCalculateDialogOpen(true)}
        onUploadCenterClick={() => handlePageChange('uploadCenter')}
        onExportClick={() => handlePageChange('reports')}
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
          width: { sm: `calc(100% - ${sidebarOpen ? 260 : 0}px - ${chatOpen ? 440 : 0}px)` },
          ml: sidebarOpen ? '260px' : 0,
          mr: { xs: 0, sm: chatOpen ? '440px' : 0 },
          transition: 'margin-left 0.3s, margin-right 0.3s, width 0.3s',
        }}
      >
        <Toolbar />
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'marketSnapshot' && <MarketSnapshot />}
        {currentPage === 'uploadCenter' && (
          <UploadCenter
            onTradingUpload={() => setUploadDialogOpen(true)}
            onWorkbookUpload={() => handlePageChange('workbooks')}
            onCalculateSchedule={() => setCalculateDialogOpen(true)}
            onAdminOpen={() => handlePageChange('adminDatabase')}
          />
        )}
        {currentPage === 'energySchedule' && <EnergySchedule />}
        {currentPage === 'analytics' && <Analytics />}
        {currentPage === 'reports' && <Reports />}
        {currentPage === 'aiPredict' && <AIPredict />}
        {currentPage === 'aiInsights' && <AIInsights />}
        {currentPage === 'adminDatabase' && (isAdmin ? <AdminDatabase /> : <Navigate to="/client/login" replace />)}
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
      <ChatAssistant open={chatOpen} onOpen={() => setChatOpen(true)} onClose={() => setChatOpen(false)} />
    </Box>
  );
};

export default AppShell;
