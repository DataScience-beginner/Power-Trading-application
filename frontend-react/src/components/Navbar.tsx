import { useState, FC } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Box,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  UploadFile as UploadFileIcon,
  Calculate as CalculateIcon,
  OpenInNew as OpenInNewIcon,
  // admin icon
  AdminPanelSettings as AdminPanelSettingsIcon,
} from '@mui/icons-material';

interface NavbarProps {
  onMenuClick: () => void;
  onUploadClick: () => void;
  onCalculateClick: () => void;
  onWorkbookInputsClick?: () => void;
  onAdminClick?: () => void;
}

const Navbar: FC<NavbarProps> = ({
  onMenuClick,
  onUploadClick,
  onCalculateClick,
  onWorkbookInputsClick,
  onAdminClick,
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

        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          Power Trading Dashboard
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Upload Inputs">
            <IconButton color="inherit" onClick={() => onWorkbookInputsClick && onWorkbookInputsClick()}>
              <OpenInNewIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Calculate Energy Schedule">
            <IconButton color="inherit" onClick={onCalculateClick}>
              <CalculateIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Upload Trading Report">
            <IconButton color="inherit" onClick={onUploadClick}>
              <UploadFileIcon />
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
