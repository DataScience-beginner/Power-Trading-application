import { FC } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import {
  Assignment,
  CloudUpload,
  Description,
  SolarPower,
  TableChart,
} from '@mui/icons-material';

interface UploadCenterProps {
  onTradingUpload: () => void;
  onWorkbookUpload: () => void;
  onCalculateSchedule: () => void;
  onAdminOpen: () => void;
}

const uploadTypes = [
  {
    title: 'DAM / RTM / GDAM',
    subtitle: 'Market trading reports',
    icon: <CloudUpload />,
    action: 'Upload Trading Report',
    helper: 'Use this for exchange market files that drive price, bid, and schedule analysis.',
    type: 'trading',
  },
  {
    title: 'SCH / DOR',
    subtitle: 'Schedule and delivery reports',
    icon: <Assignment />,
    action: 'Upload SCH / DOR',
    helper: 'Use this to compare scheduled energy versus delivered/actual positions.',
    type: 'trading',
  },
  {
    title: 'Energy Schedule Workbook',
    subtitle: 'Client planning workbook',
    icon: <TableChart />,
    action: 'Open Workbook Upload',
    helper: 'Use this for workbook-based solar working, schedule inputs, and planning sheets.',
    type: 'workbook',
  },
  {
    title: 'Solar Allocation Data',
    subtitle: 'Monthly solar validity tracking',
    icon: <SolarPower />,
    action: 'Open Workbook Upload',
    helper: 'Use this to monitor available solar, consumed solar, and month-end expiry risk.',
    type: 'workbook',
  },
  {
    title: 'Client Master Data',
    subtitle: 'Client and portfolio setup',
    icon: <Description />,
    action: 'Admin Database',
    helper: 'Use admin tools for client, portfolio, and reference-data correction.',
    type: 'admin',
  },
];

const UploadCenter: FC<UploadCenterProps> = ({
  onTradingUpload,
  onWorkbookUpload,
  onCalculateSchedule,
  onAdminOpen,
}) => {
  const handleAction = (type: string) => {
    if (type === 'workbook') {
      onWorkbookUpload();
      return;
    }

    if (type === 'trading') {
      onTradingUpload();
      return;
    }

    if (type === 'admin') {
      onAdminOpen();
    }
  };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={900}>
          Upload Center
        </Typography>
        <Typography color="text.secondary">
          Clear upload paths for trading reports, schedule files, workbooks, and client setup.
        </Typography>
      </Box>

      <Alert severity="info">
        Select the file type first, then upload against the correct client and portfolio. After
        upload, refresh dashboard data or calculate the energy schedule.
      </Alert>

      <Grid container spacing={3}>
        {uploadTypes.map((item) => (
          <Grid item xs={12} md={6} lg={4} key={item.title}>
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Stack spacing={2} sx={{ height: '100%' }}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Box sx={{ color: 'primary.main' }}>{item.icon}</Box>
                    <Box>
                      <Typography variant="h6" fontWeight={900}>
                        {item.title}
                      </Typography>
                      <Typography color="text.secondary" variant="body2">
                        {item.subtitle}
                      </Typography>
                    </Box>
                  </Stack>
                  <Typography color="text.secondary">{item.helper}</Typography>
                  <Box sx={{ flexGrow: 1 }} />
                  <Button
                    variant={item.type === 'admin' ? 'outlined' : 'contained'}
                    onClick={() => handleAction(item.type)}
                  >
                    {item.action}
                  </Button>
                  {item.type === 'admin' && <Chip label="Requires admin access" size="small" />}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card sx={{ borderRadius: 3, bgcolor: '#0f172a', color: 'white' }}>
        <CardContent sx={{ p: 3 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h6" fontWeight={900}>
                Next step after upload
              </Typography>
              <Typography color="#cbd5e1">
                Run energy schedule calculation to convert uploaded files into procurement-ready
                Solar, IEX, and TNEB planning views.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button fullWidth variant="contained" color="secondary" onClick={onCalculateSchedule}>
                Calculate Energy Schedule
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Stack>
  );
};

export default UploadCenter;
