import { useState, FC } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Box,
  Badge,
  Tooltip,
  Button,
  Stack,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  UploadFile as UploadFileIcon,
  Calculate as CalculateIcon,
  OpenInNew as OpenInNewIcon,
  AdminPanelSettings as AdminPanelSettingsIcon,
  CloudUpload as CloudUploadIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

interface NavbarProps {
  onMenuClick: () => void;
  onUploadClick: () => void;
  onCalculateClick: () => void;
  onWorkbookInputsClick?: () => void;
  onAdminClick?: () => void;
  onUploadCenterClick?: () => void;
  onExportClick?: () => void;
}

const Navbar: FC<NavbarProps> = ({
  onMenuClick,
  onUploadClick,
  onCalculateClick,
  onWorkbookInputsClick,
  onAdminClick,
  onUploadCenterClick,
  onExportClick,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 800 }}>
          Innowatt Energy AI
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Stack direction="row" spacing={1} sx={{ display: { xs: 'none', lg: 'flex' } }}>
            <Button
              color="inherit"
              variant="outlined"
              startIcon={<CloudUploadIcon />}
              onClick={() => onUploadCenterClick && onUploadCenterClick()}
              sx={{ borderColor: 'rgba(255,255,255,0.5)', textTransform: 'none', fontWeight: 700 }}
            >
              Upload Center
            </Button>
            <Button
              color="inherit"
              variant="outlined"
              startIcon={<UploadFileIcon />}
              onClick={onUploadClick}
              sx={{ borderColor: 'rgba(255,255,255,0.5)', textTransform: 'none', fontWeight: 700 }}
            >
              DAM / RTM / GDAM
            </Button>
            <Button
              color="inherit"
              variant="outlined"
              startIcon={<OpenInNewIcon />}
              onClick={() => onWorkbookInputsClick && onWorkbookInputsClick()}
              sx={{ borderColor: 'rgba(255,255,255,0.5)', textTransform: 'none', fontWeight: 700 }}
            >
              Workbook
            </Button>
            <Button
              color="inherit"
              variant="contained"
              startIcon={<CalculateIcon />}
              onClick={onCalculateClick}
              sx={{ bgcolor: 'rgba(255,255,255,0.18)', textTransform: 'none', fontWeight: 800 }}
            >
              Calculate Schedule
            </Button>
            <Button
              color="inherit"
              startIcon={<AssessmentIcon />}
              onClick={() => onExportClick && onExportClick()}
              sx={{ textTransform: 'none', fontWeight: 700 }}
            >
              Export Report
            </Button>
          </Stack>

          <Tooltip title="Upload Center">
            <IconButton
              color="inherit"
              onClick={() => onUploadCenterClick && onUploadCenterClick()}
              sx={{ display: { xs: 'inline-flex', lg: 'none' } }}
            >
              <CloudUploadIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <Badge badgeContent={0} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          <Tooltip title="Admin">
            <IconButton color="inherit" onClick={() => onAdminClick && onAdminClick()}>
              <AdminPanelSettingsIcon />
            </IconButton>
          </Tooltip>

          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleClose}>Profile</MenuItem>
            <MenuItem onClick={handleClose}>Settings</MenuItem>
            <MenuItem onClick={handleClose}>Logout</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
