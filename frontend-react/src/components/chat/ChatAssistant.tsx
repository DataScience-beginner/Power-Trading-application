import { FC, useEffect, useState } from 'react';
import { Alert, Box, Button, Chip, CircularProgress, Dialog, DialogContent, DialogTitle, Divider, Fab, MenuItem, Stack, TextField, Typography } from '@mui/material';
import { Chat, Close, Send } from '@mui/icons-material';
import apiService from '../../services/api';
import { useAppSelector } from '../../hooks/useAppStore';
import type { ChatConversation, ChatMessage, ChatUser } from '../../types/chatbot';

const ChatAssistant: FC = () => {
  const clients = useAppSelector((state) => state.dashboard.clients);
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<ChatUser | null>(null);
  const [clientId, setClientId] = useState<number | ''>('');
  const [conversation, setConversation] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    apiService.getCurrentUser().then((current) => {
      setUser(current);
      if (current.client_id) setClientId(current.client_id);
    }).catch(() => setError('Please sign in again to use the assistant.'));
  }, []);

  const ensureConversation = async () => {
    if (conversation) return conversation;
    if (!clientId) throw new Error('Select an authorized client first.');
    const created = await apiService.createChatConversation(Number(clientId));
    setConversation(created);
    return created;
  };

  const send = async (text = question) => {
    if (!text.trim()) return;
    setLoading(true); setError('');
    try {
      const active = await ensureConversation();
      const result = await apiService.sendChatMessage(active.id, text.trim());
      setMessages((current) => [...current, result.user_message, result.assistant_message]);
      setQuestion('');
    } catch (reason: any) {
      setError(String(reason?.response?.data?.detail || reason?.message || 'Chat request failed'));
    } finally { setLoading(false); }
  };

  return <>
    <Fab color="primary" onClick={() => setOpen(true)} sx={{ position: 'fixed', right: 24, bottom: 24, zIndex: 1400 }}><Chat /></Fab>
    <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm" PaperProps={{ sx: { height: '80vh' } }}>
      <DialogTitle><Stack direction="row" justifyContent="space-between"><Box><Typography fontWeight={900}>Innowatt Energy Assistant</Typography><Typography variant="caption" color="text.secondary">Scoped tools • verified facts • read-only</Typography></Box><Button onClick={() => setOpen(false)}><Close /></Button></Stack></DialogTitle>
      <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {user?.role === 'platform_admin' && <TextField select size="small" label="Client scope" value={clientId} onChange={(event) => { setClientId(Number(event.target.value)); setConversation(null); setMessages([]); }}>{clients.map((client) => <MenuItem key={client.id} value={client.id}>{client.entity_name}</MenuItem>)}</TextField>}
        {error && <Alert severity="error">{error}</Alert>}
        <Box sx={{ flex: 1, overflowY: 'auto' }}><Stack spacing={2}>
          {!messages.length && <Alert severity="info">Ask about data quality, coverage, recorded costs, or DOR/SCH data. Forecasts, bids, trades, and data changes are blocked.</Alert>}
          {messages.map((message) => <Box key={message.id} sx={{ alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '90%', bgcolor: message.role === 'user' ? 'primary.main' : 'action.hover', color: message.role === 'user' ? 'primary.contrastText' : 'text.primary', borderRadius: 3, p: 2 }}>
            <Typography sx={{ whiteSpace: 'pre-wrap' }}>{message.content}</Typography>
            {message.role === 'assistant' && <Stack direction="row" spacing={1} sx={{ mt: 1 }} flexWrap="wrap"><Chip size="small" label={message.provider || 'deterministic'} /><Chip size="small" label={`${message.confidence ?? 0}% confidence`} /><Chip size="small" color={message.safety_status === 'blocked' ? 'warning' : 'success'} label={message.safety_status} /></Stack>}
            {message.evidence.length > 0 && message.role === 'assistant' && <Typography variant="caption" display="block" sx={{ mt: 1 }}>{message.evidence.length} evidence items • {message.limitations.length} limitations</Typography>}
          </Box>)}
        </Stack></Box>
        <Divider />
        <Stack direction="row" spacing={1}><TextField fullWidth size="small" placeholder="Ask an energy data question…" value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); } }} /><Button variant="contained" onClick={() => send()} disabled={loading || !question.trim()}>{loading ? <CircularProgress size={20} /> : <Send />}</Button></Stack>
      </DialogContent>
    </Dialog>
  </>;
};

export default ChatAssistant;
