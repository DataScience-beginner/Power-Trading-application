import { FC, FormEvent, useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Container, Divider, MenuItem, Stack, TextField, Typography } from '@mui/material';
import { AdminPanelSettings, Business, Lock } from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import PublicLayout from '../../layouts/PublicLayout';
import apiService from '../../services/api';

interface LoginProps { portal: 'admin' | 'client' }

const detail = (reason: any, fallback: string) => {
  const value = reason?.response?.data?.detail;
  if (Array.isArray(value)) return value.map((item) => item.msg).join('; ');
  return String(value || fallback);
};

const Login: FC<LoginProps> = ({ portal }) => {
  const navigate = useNavigate();
  const isAdmin = portal === 'admin';
  const [email, setEmail] = useState(isAdmin ? 'admin@innowattenergy.com' : '');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('Innowatt Administrator');
  const [serviceKey, setServiceKey] = useState('');
  const [setupOpen, setSetupOpen] = useState(false);
  const [recoveryOpen, setRecoveryOpen] = useState(false);
  const [channel, setChannel] = useState<'email' | 'sms'>('email');
  const [identifier, setIdentifier] = useState(isAdmin ? 'admin@innowattenergy.com' : '');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [codeRequested, setCodeRequested] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const login = async (event: FormEvent) => {
    event.preventDefault(); setLoading(true); setError(''); setNotice('');
    try { await apiService.identityLogin(email, password, portal); navigate('/app'); }
    catch (reason) { setError(detail(reason, 'Login failed')); }
    finally { setLoading(false); }
  };

  const requestCode = async () => {
    setLoading(true); setError('');
    try { setNotice(await apiService.requestPasswordRecovery(identifier, channel, portal)); setCodeRequested(true); }
    catch (reason) { setError(detail(reason, 'Recovery request failed')); }
    finally { setLoading(false); }
  };

  const confirmRecovery = async () => {
    setLoading(true); setError('');
    try {
      setNotice(await apiService.confirmPasswordRecovery(identifier, code, newPassword, portal));
      if (channel === 'email') setEmail(identifier);
      setRecoveryOpen(false); setCodeRequested(false); setCode(''); setNewPassword('');
    } catch (reason) { setError(detail(reason, 'Recovery confirmation failed')); }
    finally { setLoading(false); }
  };

  const bootstrap = async () => {
    setLoading(true); setError('');
    try { await apiService.bootstrapAdmin(serviceKey, email, password, displayName); setNotice('First administrator created. You can now sign in.'); setSetupOpen(false); setServiceKey(''); }
    catch (reason) { setError(detail(reason, 'Administrator setup failed')); }
    finally { setLoading(false); }
  };

  return <PublicLayout><Container maxWidth="sm" sx={{ py: 8 }}><Card sx={{ borderRadius: 5 }}><CardContent sx={{ p: { xs: 3, sm: 5 } }}>
    <Stack component="form" spacing={2.5} onSubmit={login}>
      <Box>{isAdmin ? <AdminPanelSettings color="primary" sx={{ fontSize: 44 }} /> : <Business color="primary" sx={{ fontSize: 44 }} />}
        <Typography variant="h4" fontWeight={900}>{isAdmin ? 'Administrator portal' : 'Client workspace'}</Typography>
        <Typography color="text.secondary">{isAdmin ? 'Privileged access across authorized tenants.' : 'Access only your assigned client and portfolios.'}</Typography>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}{notice && <Alert severity="success">{notice}</Alert>}
      <TextField label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
      <TextField label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required helperText="Use a long, unique passphrase" />
      <Button type="submit" variant="contained" size="large" disabled={loading} startIcon={<Lock />}>Sign in</Button>
      <Button variant="text" onClick={() => setRecoveryOpen(!recoveryOpen)}>Forgot password?</Button>
      {recoveryOpen && <Stack spacing={2}>
        <Alert severity="info">A six-digit code is valid for 10 minutes. The response is identical even when an account is not eligible.</Alert>
        <TextField select label="Recovery channel" value={channel} onChange={(event) => { setChannel(event.target.value as 'email' | 'sms'); setCodeRequested(false); }}><MenuItem value="email">Verified email</MenuItem><MenuItem value="sms">Verified mobile OTP</MenuItem></TextField>
        <TextField label={channel === 'email' ? 'Account email' : 'Verified mobile (+country code)'} value={identifier} onChange={(event) => setIdentifier(event.target.value)} />
        <Button variant="outlined" onClick={requestCode} disabled={loading || identifier.length < 5}>Send recovery code</Button>
        {codeRequested && <><TextField label="Six-digit code" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))} /><TextField label="New passphrase" type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} helperText="Minimum 15 characters" /><Button variant="contained" onClick={confirmRecovery} disabled={loading || code.length !== 6 || newPassword.length < 15}>Reset password</Button></>}
      </Stack>}
      <Divider />
      <Button component={Link} to={isAdmin ? '/client/login' : '/admin/login'}>{isAdmin ? 'Go to client login' : 'Administrator login'}</Button>
      {isAdmin && <><Button variant="text" onClick={() => setSetupOpen(!setupOpen)}>First-time administrator setup</Button>{setupOpen && <Stack spacing={2}><Alert severity="warning">One-time bootstrap requires the internal service key.</Alert><TextField label="Display name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} /><TextField label="AI Foundation service key" type="password" value={serviceKey} onChange={(event) => setServiceKey(event.target.value)} /><Button variant="outlined" onClick={bootstrap} disabled={loading || !serviceKey || password.length < 10}>Create first administrator</Button></Stack>}</>}
    </Stack>
  </CardContent></Card></Container></PublicLayout>;
};

export default Login;
