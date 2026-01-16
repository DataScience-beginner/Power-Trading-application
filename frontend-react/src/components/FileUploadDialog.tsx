import { useState, FC, ChangeEvent } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  LinearProgress,
  Alert,
  Typography,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import apiService from '../services/api';

interface FileUploadDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const FileUploadDialog: FC<FileUploadDialogProps> = ({ open, onClose, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [fileType, setFileType] = useState<'DOR' | 'SCH'>('DOR');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
      setSuccess(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await apiService.uploadFile(file, fileType);
      if (result.success) {
        setSuccess(
          `File uploaded successfully! ${result.transactions_count || 0} transactions processed.`
        );
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 2000);
      } else {
        setError(result.message || 'Upload failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError(null);
    setSuccess(null);
    setUploading(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Upload Trading Report</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControl fullWidth>
            <InputLabel>File Type</InputLabel>
            <Select
              value={fileType}
              label="File Type"
              onChange={(e) => setFileType(e.target.value as 'DOR' | 'SCH')}
              disabled={uploading}
            >
              <MenuItem value="DOR">DOR (Day of Results)</MenuItem>
              <MenuItem value="SCH">SCH (Scheduled)</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUploadIcon />}
            disabled={uploading}
            fullWidth
          >
            {file ? file.name : 'Select File'}
            <input type="file" hidden accept=".pdf" onChange={handleFileChange} />
          </Button>

          {file && (
            <Typography variant="body2" color="text.secondary">
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </Typography>
          )}

          {uploading && <LinearProgress />}

          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          Cancel
        </Button>
        <Button onClick={handleUpload} variant="contained" disabled={!file || uploading}>
          Upload
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FileUploadDialog;
