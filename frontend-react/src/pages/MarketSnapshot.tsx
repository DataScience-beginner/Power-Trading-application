import { FC, useMemo, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  MenuItem,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const marketRows = [
  { block: '00:00', purchaseBid: 3174, sellBid: 878, mcv: 878, scheduled: 878, mcp: 4200, solar: 120, iex: 520, tneb: 238 },
  { block: '02:00', purchaseBid: 3053, sellBid: 867, mcv: 867, scheduled: 867, mcp: 4000, solar: 95, iex: 540, tneb: 232 },
  { block: '04:00', purchaseBid: 5585, sellBid: 1178, mcv: 1178, scheduled: 1178, mcp: 3799, solar: 170, iex: 710, tneb: 298 },
  { block: '06:00', purchaseBid: 7822, sellBid: 913, mcv: 913, scheduled: 913, mcp: 4001, solar: 340, iex: 420, tneb: 153 },
  { block: '08:00', purchaseBid: 7003, sellBid: 2168, mcv: 2168, scheduled: 2168, mcp: 2512, solar: 920, iex: 890, tneb: 358 },
  { block: '10:00', purchaseBid: 7564, sellBid: 2569, mcv: 2569, scheduled: 2569, mcp: 801, solar: 1410, iex: 790, tneb: 369 },
  { block: '12:00', purchaseBid: 7159, sellBid: 2421, mcv: 2421, scheduled: 2421, mcp: 999, solar: 1570, iex: 580, tneb: 271 },
  { block: '14:00', purchaseBid: 6789, sellBid: 2310, mcv: 2310, scheduled: 2310, mcp: 801, solar: 1490, iex: 560, tneb: 260 },
  { block: '16:00', purchaseBid: 6082, sellBid: 2065, mcv: 2065, scheduled: 2065, mcp: 1953, solar: 860, iex: 790, tneb: 415 },
  { block: '18:00', purchaseBid: 6900, sellBid: 1650, mcv: 1650, scheduled: 1650, mcp: 3600, solar: 120, iex: 1040, tneb: 490 },
  { block: '20:00', purchaseBid: 7400, sellBid: 1450, mcv: 1450, scheduled: 1450, mcp: 4200, solar: 0, iex: 980, tneb: 470 },
  { block: '22:00', purchaseBid: 5200, sellBid: 1320, mcv: 1320, scheduled: 1320, mcp: 4100, solar: 0, iex: 860, tneb: 460 },
];

const MarketSnapshot: FC = () => {
  const [tab, setTab] = useState(0);
  const metrics = useMemo(() => {
    const avgMcp = Math.round(marketRows.reduce((sum, row) => sum + row.mcp, 0) / marketRows.length);
    const totalScheduled = marketRows.reduce((sum, row) => sum + row.scheduled, 0);
    const peakDemand = Math.max(...marketRows.map((row) => row.purchaseBid));
    const solarShare = Math.round(
      (marketRows.reduce((sum, row) => sum + row.solar, 0) /
        marketRows.reduce((sum, row) => sum + row.scheduled, 0)) *
        100
    );

    return { avgMcp, totalScheduled, peakDemand, solarShare };
  }, []);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={900}>
          Market Snapshot
        </Typography>
        <Typography color="text.secondary">
          IEX-inspired view for 15-minute power-market blocks, procurement source mix, and
          schedule planning.
        </Typography>
      </Box>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
            <Button variant="contained">View Graph</Button>
            <Button variant="outlined">Update Report</Button>
            <Button variant="outlined">Export</Button>
            <TextField select label="Interval" value="15" size="small" sx={{ minWidth: 180 }}>
              <MenuItem value="15">15-Min-Block</MenuItem>
              <MenuItem value="60">Hourly</MenuItem>
            </TextField>
            <TextField select label="Delivery Period" value="today" size="small" sx={{ minWidth: 180 }}>
              <MenuItem value="today">Today</MenuItem>
              <MenuItem value="tomorrow">Tomorrow</MenuItem>
              <MenuItem value="month">This Month</MenuItem>
            </TextField>
          </Stack>
        </CardContent>
      </Card>

      <Tabs value={tab} onChange={(_, value) => setTab(value)}>
        <Tab label="Market Snapshot" />
        <Tab label="Aggregate Demand Supply" />
        <Tab label="Source Mix" />
      </Tabs>

      <Grid container spacing={2}>
        {[
          ['Avg MCP', `₹${metrics.avgMcp}/MWh`, 'Target is to buy when MCP is favorable'],
          ['Peak Purchase Bid', `${metrics.peakDemand.toLocaleString()} MW`, 'Highest demand block'],
          ['Scheduled Volume', `${metrics.totalScheduled.toLocaleString()} MW`, 'Total planned scheduled volume'],
          ['Solar Share', `${metrics.solarShare}%`, 'Day-time solar contribution in plan'],
        ].map(([label, value, note]) => (
          <Grid item xs={12} md={3} key={label}>
            <Card sx={{ borderRadius: 3, height: '100%' }}>
              <CardContent>
                <Typography color="text.secondary" variant="body2">
                  {label}
                </Typography>
                <Typography variant="h5" fontWeight={900} sx={{ mt: 1 }}>
                  {value}
                </Typography>
                <Typography color="text.secondary" variant="caption">
                  {note}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={900} gutterBottom>
                MCP price trend by block
              </Typography>
              <Box sx={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={marketRows}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="block" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="mcp" name="MCP ₹/MWh" stroke="#2563eb" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={5}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={900} gutterBottom>
                Purchase bid vs sell bid
              </Typography>
              <Box sx={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={marketRows}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="block" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="purchaseBid" name="Purchase Bid MW" fill="#0ea5e9" />
                    <Bar dataKey="sellBid" name="Sell Bid MW" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={900} gutterBottom>
                Solar / IEX / TNEB source mix with scheduled volume
              </Typography>
              <Box sx={{ height: 340 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={marketRows}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="block" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="solar" stackId="source" name="Solar MW" fill="#22c55e" />
                    <Bar dataKey="iex" stackId="source" name="IEX MW" fill="#3b82f6" />
                    <Bar dataKey="tneb" stackId="source" name="TNEB MW" fill="#f97316" />
                    <Line type="monotone" dataKey="scheduled" name="Scheduled MW" stroke="#111827" strokeWidth={3} />
                  </ComposedChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6" fontWeight={900}>
              15-minute block table
            </Typography>
            <Chip label="Sample structure" size="small" />
          </Stack>
          <Box sx={{ overflowX: 'auto' }}>
            <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse', minWidth: 900 }}>
              <Box component="thead" sx={{ bgcolor: '#f1f5f9' }}>
                <Box component="tr">
                  {['Time Block', 'Purchase Bid MW', 'Sell Bid MW', 'MCV MW', 'Scheduled MW', 'Solar MW', 'IEX MW', 'TNEB MW', 'MCP ₹/MWh'].map((head) => (
                    <Box component="th" key={head} sx={{ p: 1.5, textAlign: 'left', fontSize: 13 }}>
                      {head}
                    </Box>
                  ))}
                </Box>
              </Box>
              <Box component="tbody">
                {marketRows.map((row) => (
                  <Box component="tr" key={row.block} sx={{ borderTop: '1px solid #e2e8f0' }}>
                    <Box component="td" sx={{ p: 1.5 }}>{row.block}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>{row.purchaseBid.toLocaleString()}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>{row.sellBid.toLocaleString()}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>{row.mcv.toLocaleString()}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>{row.scheduled.toLocaleString()}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>{row.solar.toLocaleString()}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>{row.iex.toLocaleString()}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>{row.tneb.toLocaleString()}</Box>
                    <Box component="td" sx={{ p: 1.5 }}>₹{row.mcp.toLocaleString()}</Box>
                  </Box>
                ))}
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Stack>
  );
};

export default MarketSnapshot;
