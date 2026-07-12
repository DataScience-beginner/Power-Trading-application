import { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import apiService from '../services/api';

interface Enrollment {
  factor_id: string;
  secret: string;
  provisioning_uri: string;
  message: string;
}

const SecuritySettings = () => {
  const [enrollment, setEnrollment] = useState<Enrollment | null>(null);
  const [code, setCode] = useState('');
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([]);
  const [error, setError] = useState('');

  const begin = async () => {
    setError(''); setRecoveryCodes([]);
    try { setEnrollment(await apiService.beginMfaEnrollment()); }
    catch (reason: any) { setError(String(reason?.response?.data?.detail || 'MFA enrollment failed')); }
  };

  const verify = async () => {
    setError('');
    try {
      const result = await apiService.verifyMfaEnrollment(code);
      setRecoveryCodes(result.recovery_codes); setEnrollment(null); setCode('');
    } catch (reason: any) { setError(String(reason?.response?.data?.detail || 'MFA verification failed')); }
  };

  return <Box><Typography variant="h4" fontWeight={800} mb={3}>Security settings</Typography>
    <Card><CardContent><Stack spacing={2}>
      <Typography variant="h6">Authenticator MFA</Typography>
      <Typography color="text.secondary">Protect this account with a time-based code from your authenticator application.</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      {!enrollment && recoveryCodes.length === 0 && <Button variant="contained" onClick={begin}>Set up authenticator MFA</Button>}
      {enrollment && <>
        <Alert severity="warning">Add this secret or provisioning URI to your authenticator. It is displayed only during enrollment.</Alert>
        <TextField label="Authenticator secret" value={enrollment.secret} InputProps={{ readOnly: true }} />
        <TextField label="Provisioning URI" value={enrollment.provisioning_uri} multiline InputProps={{ readOnly: true }} />
        <TextField label="Six-digit verification code" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))} />
        <Button variant="contained" disabled={code.length !== 6} onClick={verify}>Verify and enable MFA</Button>
      </>}
      {recoveryCodes.length > 0 && <Alert severity="success">
        MFA is enabled. Store these single-use recovery codes offline: {recoveryCodes.join(', ')}
      </Alert>}
    </Stack></CardContent></Card>
  </Box>;
};

export default SecuritySettings;
