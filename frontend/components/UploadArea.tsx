import React from 'react';
import { 
    Paper, 
    Box, 
    Typography, 
    Button, 
    LinearProgress, 
    Alert 
} from '@mui/material';
import { Upload } from "lucide-react";
import type { FileRejection, DropzoneOptions } from 'react-dropzone';
import { useDropzone } from 'react-dropzone';

interface UploadAreaProps {
    onUpload: (file: File) => Promise<void>;
    isUploading: boolean;
    error?: string | null;
}

export const UploadArea: React.FC<UploadAreaProps> = ({ onUpload, isUploading, error }) => {
    const dropzoneOptions: DropzoneOptions = {
        accept: {
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png']
        },
        multiple: false,
        disabled: isUploading,
        onDrop: async (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
            try {
                if (acceptedFiles?.[0]) {
                    console.log('File selected:', acceptedFiles[0].name);
                    await onUpload(acceptedFiles[0]);
                }
            } catch (error) {
                console.error('Upload error:', error);
            }
        }
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone(dropzoneOptions);

    return (
        <Paper 
            {...getRootProps()}
            variant="outlined" 
            sx={{ 
                p: { xs: 1.5, sm: 2, md: 4 },
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: { xs: 1, sm: 2 },
                borderStyle: 'dashed',
                position: 'relative',
                cursor: 'pointer',
                borderColor: isDragActive ? 'primary.main' : 'divider',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                transition: 'all 0.2s ease',
                '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.hover'
                },
                border: 'none',
                '& .MuiPaper-root': {
                    border: 'none'
                }
            }}
        >
            <input {...getInputProps()} />
            
            {isUploading && (
                <LinearProgress 
                    sx={{ 
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        borderTopLeftRadius: 'inherit',
                        borderTopRightRadius: 'inherit'
                    }}
                />
            )}
            
            <Box 
                sx={{ 
                    bgcolor: 'action.hover',
                    borderRadius: '50%',
                    p: { xs: 1.5, sm: 2 },
                    display: 'flex'
                }}
            >
                <Upload size={24} />
            </Box>

            <Button
                variant="contained"
                component="span"
                startIcon={<Upload size={16} />}
                disabled={isUploading}
                sx={{
                    width: { xs: '100%', sm: 'auto' },
                    minHeight: { xs: 40, sm: 36 },
                    fontSize: { xs: '0.8125rem', sm: '0.875rem' }
                }}
            >
                {isUploading ? 'Uploading...' : 'Upload Receipt'}
            </Button>

            <Typography 
                variant="body2" 
                color="text.secondary"
                align="center"
                sx={{ 
                    fontSize: { xs: '0.75rem', sm: '0.875rem' }
                }}
            >
                {isDragActive 
                    ? 'Drop the receipt here...'
                    : isUploading 
                        ? 'Processing your receipt...' 
                        : 'Supported formats: JPEG, PNG'
                }
            </Typography>

            {error && (
                <Alert 
                    severity="error" 
                    sx={{ 
                        width: '100%',
                        mt: { xs: 1, sm: 2 }
                    }}
                >
                    {error}
                </Alert>
            )}
        </Paper>
    );
}; 