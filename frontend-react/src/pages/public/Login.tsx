import { FC, FormEvent, useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Container, Divider, Stack, TextField, Typography } from '@mui/material';
import { Lock } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import PublicLayout from '../../layouts/PublicLayout';
import apiService from '../../services/api';

const Login: FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('Innowatt Administrator');
  const [serviceKey, setServiceKey] = useState('');
  const [setupOpen, setSetupOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const login = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true); setError(''); setNotice('');
    try {
      await apiService.login(email, password);
      navigate('/app');
    } catch (reason: any) {
      setError(String(reason?.response?.data?.detail || 'Login failed'));
    } finally { setLoading(false); }
  };

  const bootstrap = async () => {
    setLoading(true); setError(''); setNotice('');
    try {
      await apiService.bootstrapAdmin(serviceKey, email, password, displayName);
      setNotice('First administrator created. You can now sign in.');
      setSetupOpen(false);
      setServiceKey('');
    } catch (reason: any) {
      setError(String(reason?.response?.data?.detail || 'Administrator setup failed'));
    } finally { setLoading(false); }
  };

  return (
    <PublicLayout>
      <Container maxWidth="sm" sx={{ py: 10 }}>
        <Card sx={{ borderRadius: 5 }}><CardContent sx={{ p: 5 }}>
          <Stack component="form" spacing={3} onSubmit={login}>
            <Box><Lock color="primary" sx={{ fontSize: 42 }} /><Typography variant="h4" fontWeight={900}>Sign in to Innowatt</Typography><Typography color="text.secondary">Your role controls which clients and portfolios the assistant can access.</Typography></Box>
            {error && <Alert severity="error">{error}</Alert>}
            {notice && <Alert severity="success">{notice}</Alert>}
            <TextField label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            <TextField label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required helperText="Minimum 10 characters" />
            <Button type="submit" variant="contained" size="large" disabled={loading}>Sign in</Button>
            <Divider>First-time setup</Divider>
            <Button variant="text" onClick={() => setSetupOpen(!setupOpen)}>Bootstrap first administrator</Button>
            {setupOpen && <Stack spacing={2}>
              <Alert severity="warning">This works only once and requires the internal AI Foundation service key.</Alert>
              <TextField label="Display name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
              <TextField label="AI Foundation service key" type="password" value={serviceKey} onChange={(event) => setServiceKey(event.target.value)} />
              <Button variant="outlined" onClick={bootstrap} disabled={loading || !serviceKey || password.length < 10}>Create first administrator</Button>
            </Stack>}
          </Stack>
        </CardContent></Card>
      </Container>
    </PublicLayout>
  );
};

export default Login;
