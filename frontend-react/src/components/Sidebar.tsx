import { useEffect, FC, useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  Collapse,
  Typography,
  Box,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Folder as FolderIcon,
  ExpandLess,
  ExpandMore,
  Business as BusinessIcon,
  CalendarMonth as CalendarIcon,
  Psychology as PsychologyIcon
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../hooks/useAppStore';
import { fetchClients } from '../store/dashboardSlice';

const drawerWidth = 260;
  const isAdmin = Boolean(localStorage.getItem('admin_jwt') || sessionStorage.getItem('admin_jwt'));

export type AppPage = 'dashboard' | 'energySchedule' | 'analytics' | 'reports' | 'aiPredict' | 'adminDatabase' | 'newDashboard' | 'workbooks';

interface SidebarProps {
  open: boolean;
  onPortfolioSelect: (portfolio: string) => void;
  currentPage: AppPage;
  onPageChange: (page: AppPage) => void;
}

const Sidebar: FC<SidebarProps> = ({ open, onPortfolioSelect, currentPage, onPageChange }) => {
  // Only show admin menu if JWT is present
  const isAdmin = Boolean(localStorage.getItem('admin_jwt') || sessionStorage.getItem('admin_jwt'));
  const dispatch = useAppDispatch();
  const { clients } = useAppSelector((state) => state.dashboard);
  const [openClients, setOpenClients] = useState(true);
  const [selectedClient, setSelectedClient] = useState<number | null>(null);

  useEffect(() => {
    dispatch(fetchClients());
  }, [dispatch]);

  const handleClickClients = () => {
    setOpenClients(!openClients);
  };
  
  const handleClientClick = (clientId: number, clientName: string) => {
    setSelectedClient(clientId);
    onPortfolioSelect(clientName); // This will filter dashboard data
  };

  // Extract unique portfolios from clients
  const portfolios = clients.flatMap((client) =>
    // You'd need to modify API to return portfolios with clients
    // For now, we'll just show clients
    []
  );

  return (
    <Drawer
      variant="persistent"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          <ListItem disablePadding>
            <ListItemButton 
              selected={currentPage === 'dashboard'}
              onClick={() => onPageChange('dashboard')}
            >
              <ListItemIcon>
                <DashboardIcon color={currentPage === 'dashboard' ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              selected={currentPage === 'energySchedule'}
              onClick={() => onPageChange('energySchedule')}
            >
              <ListItemIcon>
                <CalendarIcon color={currentPage === 'energySchedule' ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText primary="Energy Schedule" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              selected={currentPage === 'analytics'}
              onClick={() => onPageChange('analytics')}
            >
              <ListItemIcon>
                <TrendingUpIcon color={currentPage === 'analytics' ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText primary="Analytics" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              selected={currentPage === 'reports'}
              onClick={() => onPageChange('reports')}
            >
              <ListItemIcon>
                <AssessmentIcon color={currentPage === 'reports' ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText primary="Reports" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              selected={currentPage === 'aiPredict'}
              onClick={() => onPageChange('aiPredict')}
            >
              <ListItemIcon>
                <PsychologyIcon color={currentPage === 'aiPredict' ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText primary="🤖 AI Predict" />
            </ListItemButton>
          </ListItem>
        </List>
        {isAdmin && (
          <List>
            <ListItem disablePadding>
              <ListItemButton
                selected={currentPage === 'adminDatabase'}
                onClick={() => {
                  onPageChange('adminDatabase');
                  try {
                    // update URL so App can react to navigation if needed
                    const url = new URL(window.location.href);
                    url.searchParams.set('page', 'adminDatabase');
                    window.history.pushState({}, '', url.toString());
                  } catch (e) {
                    // ignore
                  }
                }}
              >
                <ListItemIcon>
                  <StorageIcon color={currentPage === 'adminDatabase' ? 'primary' : 'inherit'} />
                </ListItemIcon>
                <ListItemText primary="Admin Database" />
              </ListItemButton>
            </ListItem>
          </List>
        )}

        <Divider />

        <List>
          <ListItemButton onClick={handleClickClients}>
            <ListItemIcon>
              <BusinessIcon />
            </ListItemIcon>
            <ListItemText primary="Clients" />
            {openClients ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>

          <Collapse in={openClients} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {clients.length === 0 ? (
                <ListItem sx={{ pl: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No clients found
                  </Typography>
                </ListItem>
              ) : (
                clients.map((client) => (
                  <ListItem key={client.id} disablePadding>
                    <ListItemButton 
                      sx={{ 
                        pl: 4,
                        backgroundColor: selectedClient === client.id ? 'action.selected' : 'transparent'
                      }}
                      onClick={() => handleClientClick(client.id, client.entity_name)}
                    >
                      <ListItemIcon>
                        <FolderIcon fontSize="small" color={selectedClient === client.id ? 'primary' : 'inherit'} />
                      </ListItemIcon>
                      <ListItemText
                        primary={client.entity_name}
                        secondary={`${client.portfolio_count || 0} portfolios`}
                        primaryTypographyProps={{ 
                          fontSize: '0.875rem',
                          fontWeight: selectedClient === client.id ? 600 : 400
                        }}
                        secondaryTypographyProps={{ fontSize: '0.75rem' }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))
              )}
            </List>
          </Collapse>
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
