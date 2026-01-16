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
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Folder as FolderIcon,
  ExpandLess,
  ExpandMore,
  Business as BusinessIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../hooks/useAppStore';
import { fetchClients } from '../store/dashboardSlice';

const drawerWidth = 260;

interface SidebarProps {
  open: boolean;
  onPortfolioSelect: (portfolio: string) => void;
}

const Sidebar: FC<SidebarProps> = ({ open, onPortfolioSelect }) => {
  const dispatch = useAppDispatch();
  const { clients } = useAppSelector((state) => state.dashboard);
  const [openClients, setOpenClients] = useState(true);

  useEffect(() => {
    dispatch(fetchClients());
  }, [dispatch]);

  const handleClickClients = () => {
    setOpenClients(!openClients);
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
            <ListItemButton>
              <ListItemIcon>
                <DashboardIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <TrendingUpIcon />
              </ListItemIcon>
              <ListItemText primary="Analytics" />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <AssessmentIcon />
              </ListItemIcon>
              <ListItemText primary="Reports" />
            </ListItemButton>
          </ListItem>
        </List>

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
                    <ListItemButton sx={{ pl: 4 }}>
                      <ListItemIcon>
                        <FolderIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={client.entity_name}
                        secondary={`${client.portfolio_count} portfolios`}
                        primaryTypographyProps={{ fontSize: '0.875rem' }}
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
