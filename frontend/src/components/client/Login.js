import React from 'react';
import { Container, Box, TextField, Typography } from '@mui/material';

const Login = () => {
    return (
        <Container
            sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
            }}
        >
            <Typography variant="h4" gutterBottom>
                Welcome
            </Typography>
            <Box
                component="form"
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                    width: '300px',
                }}
            >
                <TextField label="Username" variant="outlined" fullWidth />
                <TextField label="Access Code" variant="outlined" fullWidth type="password" />
            </Box>
        </Container>
    );
};

export default Login;